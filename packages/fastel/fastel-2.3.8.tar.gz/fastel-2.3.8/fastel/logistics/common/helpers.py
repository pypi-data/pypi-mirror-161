from typing import Any, Dict, List, Tuple, Union

import boto3
from bs4 import BeautifulSoup
from fastapi import Response
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from requests import Response as ResponseType

from fastel.collections import get_collection, get_site_config
from fastel.config import SdkConfig
from fastel.exceptions import APIException
from fastel.logistics.common.models import (
    LogisticsDataModel,
    LogisticsStatus,
    LogisticTypes,
)
from fastel.logistics.ecpay.gateway import EcpayLogistics
from fastel.logistics.ecpay.models import (
    CvsMapSubTypeOptions,
    CVSSubtypes,
    EcpayCVSMapModel,
    EcpayLogisticsCallbackModel,
    EcpayLogisticsModel,
    EcpayPrintOrderInfo,
)
from fastel.logistics.sf.gateway import SFLogistics
from fastel.logistics.sf.models import SFLogisticsModel
from fastel.payment.common.models.order import Order, ProductItem
from fastel.utils import requests, timestamp_postfix


class EcpayLogisticsCreate:
    def __init__(self, callback_url: str) -> None:
        self.gateway = EcpayLogistics(
            merchant_id=SdkConfig.ecpay_logistics_merchant_id,
            hash_key=SdkConfig.ecpay_logistics_hash_key,
            hash_iv=SdkConfig.ecpay_logistics_hash_iv,
            stage=SdkConfig.stage,
        )
        self.server_reply_url = callback_url

    def __call__(
        self, order: Dict[str, Any], extra_data: Dict[str, Any] = {}
    ) -> LogisticsDataModel:
        validated = self.validate(order)
        parser = self.parse_logistics(validated, extra_data)
        gateway_resp = self.gateway.create_logistics(data=parser)
        result = self.parse_gateway_resp(gateway_resp=gateway_resp)
        return result

    @staticmethod
    def validate(order: Dict[str, Any]) -> Order:
        return Order.validate(order)

    @staticmethod
    def _replace_limit_name(name: str, limit: int) -> str:
        if len(name) > limit:
            return name[: limit - 3] + "..."
        return name

    def parse_logistics(
        self, order: Order, extra_data: Dict[str, Any]
    ) -> EcpayLogisticsModel:
        if order.total > 20000:
            APIException(
                status_code=400, error="validation_error", detail="物流訂單商品不能超過20000元新台幣"
            )
        counter = get_collection("counter").find_one_and_update(
            {"collection": "logistics", "order_id": order.order_id},
            {
                "$inc": {"idx": 1},
                "$setOnInsert": {"collection": "logistics", "order_id": order.order_id},
            },
            upsert=True,
        )
        if not counter:
            counter = {"idx": 0}
        common_props = dict(
            MerchantTradeNo=f"{order.order_id}_{counter['idx'] + 1}",
            GoodsName=f"訂單{order.order_id}",
            GoodsAmount=order.total,
            ReceiverName=self._replace_limit_name(name=order.receiver_name, limit=10),
            ReceiverEmail=order.receiver_email,
            ReceiverCellPhone=order.receiver_phone,
            ReceiverZipCode=order.receiver_zip,
            ReceiverAddress=(
                order.receiver_city + order.receiver_district + order.receiver_address
            ),
            ServerReplyURL=self.server_reply_url,
        )

        default_sender_info = dict(
            SenderName="忻旅科技",
            SenderPhone="02-77295130",
            SenderZipCode="10361",
            SenderCellPhone="0900000000",
            SenderAddress="台北市大同區民權西路136號10樓之5",
        )

        sender_info = get_site_config(
            key="logistics_sender_info", default=default_sender_info
        )
        sender_info["SenderName"] = self._replace_limit_name(
            name=sender_info["SenderName"], limit=10
        )
        data: EcpayLogisticsModel
        if order.logistics_type == "HOME":
            data = EcpayLogisticsModel(
                **common_props,
                **sender_info,
                **extra_data,
                Distance=("00" if order.receiver_city == "台北市" else "01"),
                Temperature="0001",
            )
        elif order.logistics_type == "CVS":
            data = EcpayLogisticsModel(
                **common_props,
                **sender_info,
                **extra_data,
                LogisticsType="CVS",
                LogisticsSubType=order.logistics_subtype,
                IsCollection="Y" if order.payment_subtype == "cod" else "N",
                CollectionAmount=order.total if order.payment_subtype == "cod" else 0,
                ReceiverStoreID=order.logistics_cvs_store_id,
            )
        else:
            raise APIException(
                status_code=400,
                error="validation_error",
                detail=f"not found logistics_type {order.logistics_type}",
            )
        return data

    @staticmethod
    def parse_gateway_resp(gateway_resp: Dict[str, Any]) -> LogisticsDataModel:
        if gateway_resp.get("error", {}):
            error = "error"
            error_msg = gateway_resp["error"]
            return LogisticsDataModel(
                provider="ecpay",
                order_id=error,
                logistics_id=error,
                logistics_type=LogisticTypes.UNKNOWN,
                logistics_subtype="",
                logistics_status=LogisticsStatus.error,
                logistics_message=error_msg,
                logistics_detail=gateway_resp,
            )

        return LogisticsDataModel(
            provider="ecpay",
            order_id=gateway_resp["MerchantTradeNo"].split("_")[0],
            logistics_id=gateway_resp["AllPayLogisticsID"],
            logistics_type=gateway_resp["LogisticsType"],
            logistics_subtype=gateway_resp["LogisticsSubType"],
            logistics_status=LogisticsStatus.pending,
            logistics_message=gateway_resp["RtnMsg"],
            logistics_detail=gateway_resp,
        )


class EcpayLogisticsCallback:
    def __init__(self) -> None:
        self.gateway = EcpayLogistics(
            merchant_id=SdkConfig.ecpay_logistics_merchant_id,
            hash_key=SdkConfig.ecpay_logistics_hash_key,
            hash_iv=SdkConfig.ecpay_logistics_hash_iv,
            stage=SdkConfig.stage,
        )
        self.response = "0|NOPE"

    def __call__(self, data: Dict[str, Any]) -> LogisticsDataModel:
        validated = self.validate(data)
        self.check_mac_data(data=validated)
        parsed = self.parse_payload(validated)
        return parsed

    async def parse_request(self, request: Request) -> Dict[str, Any]:
        data = await request.form()
        return requests.parse_formdata(data)

    def validate(self, data: Dict[str, Any]) -> EcpayLogisticsCallbackModel:
        return EcpayLogisticsCallbackModel.validate(data)

    def check_mac_data(self, data: EcpayLogisticsCallbackModel) -> None:
        mac_value = data.CheckMacValue
        result_data = data.dict(exclude_none=True)
        result_data.pop("CheckMacValue", None)

        result = self.gateway.cryptor.encrypt(result_data)
        if result == mac_value:
            self.response = "1|OK"

    def parse_payload(self, result: EcpayLogisticsCallbackModel) -> LogisticsDataModel:
        if result.LogisticsType == "HOME":
            home_status_table = {
                "300": LogisticsStatus.pending,
                "310": LogisticsStatus.pending,
                "3001": LogisticsStatus.center_delivered,
                "3003": LogisticsStatus.delivered,
                "3006": LogisticsStatus.in_delivery,
            }
            try:
                print(result.RtnCode)
                logistics_status = home_status_table[result.RtnCode]
            except KeyError:
                logistics_status = LogisticsStatus.exception
        else:
            cvs_status_table: Dict[str, Any] = {
                CVSSubtypes.FAMIC2C: {
                    "300": LogisticsStatus.pending,
                    "310": LogisticsStatus.pending,
                    "3024": LogisticsStatus.center_delivered,
                    "3018": LogisticsStatus.store_delivered,
                    "3022": LogisticsStatus.delivered,
                },
                CVSSubtypes.UNIMARTC2C: {
                    "300": LogisticsStatus.pending,
                    "310": LogisticsStatus.pending,
                    "2030": LogisticsStatus.center_delivered,
                    "2073": LogisticsStatus.store_delivered,
                    "2067": LogisticsStatus.delivered,
                },
                CVSSubtypes.HILIFEC2C: {
                    "300": LogisticsStatus.pending,
                    "310": LogisticsStatus.pending,
                    "2001": LogisticsStatus.pending,
                    "2030": LogisticsStatus.center_delivered,
                    "3024": LogisticsStatus.center_delivered,
                    "2063": LogisticsStatus.store_delivered,
                    "3018": LogisticsStatus.store_delivered,
                    "2067": LogisticsStatus.delivered,
                    "3022": LogisticsStatus.delivered,
                },
                CVSSubtypes.OKMARTC2C: {
                    "300": LogisticsStatus.pending,
                    "310": LogisticsStatus.pending,
                    "2030": LogisticsStatus.center_delivered,
                    "2073": LogisticsStatus.store_delivered,
                    "3022": LogisticsStatus.delivered,
                },
                CVSSubtypes.FAMI: {
                    "300": LogisticsStatus.pending,
                    "310": LogisticsStatus.pending,
                    "3024": LogisticsStatus.center_delivered,
                    "3018": LogisticsStatus.store_delivered,
                    "3022": LogisticsStatus.delivered,
                },
                CVSSubtypes.UNIMART: {
                    "300": LogisticsStatus.pending,
                    "310": LogisticsStatus.pending,
                    "2030": LogisticsStatus.center_delivered,
                    "2073": LogisticsStatus.store_delivered,
                    "2067": LogisticsStatus.delivered,
                },
                CVSSubtypes.HILIFE: {
                    "300": LogisticsStatus.pending,
                    "310": LogisticsStatus.pending,
                    "2001": LogisticsStatus.pending,
                    "2030": LogisticsStatus.center_delivered,
                    "3024": LogisticsStatus.center_delivered,
                    "2063": LogisticsStatus.store_delivered,
                    "3018": LogisticsStatus.store_delivered,
                    "2067": LogisticsStatus.delivered,
                    "3022": LogisticsStatus.delivered,
                },
            }

            try:
                logistics_status = cvs_status_table[result.LogisticsSubType][
                    result.RtnCode
                ]
            except KeyError:
                logistics_status = LogisticsStatus.exception

        return LogisticsDataModel(
            provider="ecpay",
            order_id=result.MerchantTradeNo.split("_")[0],
            logistics_id=result.AllPayLogisticsID,
            logistics_type=result.LogisticsType,
            logistics_subtype=result.LogisticsSubType,
            logistics_status=logistics_status,
            logistics_message=result.RtnMsg,
            logistics_payment_no=result.CVSPaymentNo,
            logistics_validate_no=result.CVSValidationNo,
        )

    def respond(self, **kwargs: Any) -> Response:
        return Response(content=self.response)


class EcpayGetShippingNote:
    def __init__(self) -> None:
        self.gateway = EcpayLogistics(
            merchant_id=SdkConfig.ecpay_logistics_merchant_id,
            hash_key=SdkConfig.ecpay_logistics_hash_key,
            hash_iv=SdkConfig.ecpay_logistics_hash_iv,
            stage=SdkConfig.stage,
        )

    def __call__(self, data: Dict[str, Any]) -> Tuple[bytes, str]:
        validated = self.validate(data)
        parsed = self.parse_payload(validated)
        html, logistics_subtype = self.gateway.get_shipping_note(parsed)
        print(html)
        if logistics_subtype == "UniMartC2C":
            return html.encode(), "text/html"
        else:
            img_url = self.fetch_html_img(html)
            print("shipping note url:", img_url)
            img_url = img_url.replace("amp;", "")
            img_resp: ResponseType = requests.get(img_url)
            img_resp.raise_for_status()
            img = img_resp.content
            content_type = img_resp.headers.get("Content-Type", "image/png")
        return img, content_type

    @staticmethod
    def fetch_html_img(html: str) -> str:
        soup = BeautifulSoup(html)
        img_tag = soup.find("img")
        if not img_tag:
            form = soup.find("form")
            if not form:
                return ""
            else:
                return str(form.get("action", ""))
        else:
            return str(img_tag.get("src", ""))

    def validate(self, data: Dict[str, Any]) -> LogisticsDataModel:
        return LogisticsDataModel.validate(data)

    def parse_payload(self, result: LogisticsDataModel) -> EcpayPrintOrderInfo:
        if result.logistics_subtype == "UNIMARTC2C":
            payload = {
                "LogisticsSubType": "UniMartC2C",
                "AllPayLogisticsID": result.logistics_id,
                "CVSPaymentNo": result.logistics_payment_no,
                "CVSValidationNo": result.logistics_validate_no,
            }
        elif result.logistics_subtype in ["FAMIC2C", "OKMARTC2C", "HILIFEC2C"]:
            payload = {
                "LogisticsSubType": result.logistics_subtype,
                "AllPayLogisticsID": result.logistics_id,
                "CVSPaymentNo": result.logistics_payment_no,
            }
        elif result.logistics_subtype in [
            "FAMI",
            "UNIMART",
            "UNIMARTFREEZE",
            "HILIFE",
            "TCAT",
            "ECAN",
        ]:
            payload = {
                "LogisticsSubType": result.logistics_subtype,
                "AllPayLogisticsID": result.logistics_id,
            }

        return EcpayPrintOrderInfo.validate(payload)


class SFLogisticsCreate:
    def __init__(self) -> None:
        self.gateway = SFLogistics(
            merchant_id=SdkConfig.sf_merchant_id,
            aes_key=SdkConfig.sf_aes_key,
            app_key=SdkConfig.sf_app_key,
            secret=SdkConfig.sf_secret,
            stage=SdkConfig.stage,
        )

    def __call__(
        self, order: Dict[str, Any], extra_data: Dict[str, Any] = {}
    ) -> LogisticsDataModel:
        validated = self.validate(order)
        parsed = self.parse_logistics(validated, extra_data)
        gateway_resp = self.gateway.create_logistics(parsed)
        result = self.parse_gateway_resp(gateway_resp=gateway_resp)
        return result

    @staticmethod
    def validate(order: Dict[str, Any]) -> Order:
        return Order.validate(order)

    @staticmethod
    def generate_items(items: List[ProductItem]) -> List[Dict[str, Any]]:
        result = []
        for item in items:
            data = {
                "name": item.name,
                "unit": "個",
                "amount": float(item.amount),
                "currency": "NTD",
                "quantity": float(item.config.qty),
                "originCountry": "TW",
            }
            result.append(data)
        return result

    def parse_logistics(
        self, order: Order, extra_data: Dict[str, Any]
    ) -> SFLogisticsModel:
        default_sender_info = dict(
            SenderName="忻旅科技",
            SenderPhone="02-77295130",
            SenderZipCode="10361",
            SenderCellPhone="0900000000",
            SenderAddress="台北市大同區民權西路136號10樓之5",
        )
        sender_info: Dict[str, Any] = get_site_config(
            key="logistics_sender_info", default=default_sender_info
        )
        payload = {
            "customerCode": SdkConfig.sf_merchant_id,
            "orderOperateType": 1,
            "customerOrderNo": order.order_id,
            "interProductCode": extra_data.get("platform_code", "INT0005"),
            # 包裹數 *
            "parcelQuantity": extra_data.get("parcel_quantity", 1),
            # 聲明價值 * order
            "declaredValue": order.total,
            # 包裹总计声明价值币种
            "declaredCurrency": "NTD",
            # 寄件方式 0: 服務點自寄或自行聯繫快遞員 1: 上門收件
            "pickupType": "1",
            # 上門區間預約時間 yyyy-MM-dd HH:mm 如果pickupType 為 1 則必填
            "pickupAppointTime": extra_data.get("pickup_time"),
            # 收件時區
            "pickupAppointTimeZone": "Asia/Taipei",
            # 運單備註 *
            "remark": extra_data.get("note", ""),
            # 付款方式
            "paymentInfo": {
                # 付款方式 1 寄方付， 2 收方付， 3 第三方付
                "payMethod": "3",
                "taxPayMethod": "3",
                "payMonthCard": SdkConfig.sf_card_no,
            },
            # 寄件人訊息
            "senderInfo": {
                # 寄件人名字
                "contact": sender_info.get("SenderName", ""),
                # 寄件國家/地區
                "country": "TW",
                # 郵編
                "postCode": sender_info.get("SenderZipCode", ""),
                # 州/省
                "regionFirst": "台灣省",
                # 城市
                "regionSecond": sender_info.get("SenderCity", "臺北市"),
                # 區
                "regionThird": sender_info.get("SenderDistrict", "大同區"),
                "address": sender_info.get("SenderAddress", ""),
                "email": sender_info.get("SenderEmail", ""),
                "cargoType": extra_data.get("cargo_type", 1),
                "telNo": sender_info.get("SenderPhone", ""),
            },
            # 收件人訊息
            "receiverInfo": {
                # 寄件人名字
                "contact": order.receiver_name,
                # 寄件國家/地區
                "country": "TW",
                # 郵編
                "postCode": order.receiver_zip,
                # 州/省
                "regionFirst": "台灣省",
                # 城市
                "regionSecond": order.receiver_city,
                # 區
                "regionThird": order.receiver_district,
                "address": order.receiver_address,
                "email": order.receiver_email,
                "cargoType": extra_data.get("cargo_type", 1),
                "phoneNo": order.receiver_phone,
            },
            # 包裹訊息
            "parcelInfoList": self.generate_items(order.items),
        }

        return SFLogisticsModel.validate(payload)

    @staticmethod
    def parse_gateway_resp(gateway_resp: Dict[str, Any]) -> LogisticsDataModel:
        resp_data = gateway_resp.get("data", {})
        if gateway_resp.get("success", False):
            logistics_id = resp_data.get("sfWaybillNo", "")
            logistics_status = LogisticsStatus.pending
            logistics_message = "訂單處理中(已收到訂單資料)"

        else:
            logistics_id = ""
            logistics_status = LogisticsStatus.error
            logistics_message = gateway_resp.get("msg", "")

        return LogisticsDataModel(
            provider="sf",
            order_id=resp_data.get("customerOrderNo", ""),
            logistics_id=logistics_id,
            logistics_type="HOME",
            logistics_subtype="SF",
            logistics_status=logistics_status,
            logistics_message=logistics_message,
        )


class SFLogisticsStatus:
    def __init__(self) -> None:
        self.gateway = SFLogistics(
            merchant_id=SdkConfig.sf_merchant_id,
            aes_key=SdkConfig.sf_aes_key,
            app_key=SdkConfig.sf_app_key,
            secret=SdkConfig.sf_secret,
            stage=SdkConfig.stage,
        )

    def __call__(self, logistics_id: str) -> LogisticsDataModel:
        parsed = self.parse_data(logistics_id)
        gateway_resp = self.gateway.query_track(parsed)
        result = self.parse_gateway_resp(gateway_resp=gateway_resp)
        return result

    @staticmethod
    def parse_data(logistics_id: str) -> Dict[str, Any]:
        data = {"customerCode": SdkConfig.sf_merchant_id, "sfWaybillNo": logistics_id}
        return data

    @staticmethod
    def parse_gateway_resp(gateway_resp: Dict[str, Any]) -> LogisticsDataModel:
        resp_data = gateway_resp.get("data", {})
        if gateway_resp.get("success", False):
            track_data: Dict[str, Any] = resp_data.get("tackDetailItems", [])[0]
            logistics_id = resp_data.get("sfWaybillNo", "")
            logistics_status = LogisticsStatus.pending
            logistics_message = track_data.get("trackOutRemark", "")

        else:
            logistics_id = resp_data.get("sfWaybillNo", "")
            logistics_status = LogisticsStatus.exception
            logistics_message = gateway_resp.get("msg", "")

        return LogisticsDataModel(
            provider="sf",
            order_id="",
            logistics_id=logistics_id,
            logistics_type="HOME",
            logistics_subtype="SF",
            logistics_status=logistics_status,
            logistics_message=logistics_message,
        )


class EcpayLogisticsMap:
    def __init__(self, callback_url: str) -> None:
        self.gateway = EcpayLogistics(
            merchant_id=SdkConfig.ecpay_logistics_merchant_id,
            hash_key=SdkConfig.ecpay_logistics_hash_key,
            hash_iv=SdkConfig.ecpay_logistics_hash_iv,
            stage=SdkConfig.stage,
        )
        self.server_reply_url = callback_url

    def __call__(
        self, logistics_subtype: CvsMapSubTypeOptions, is_collection: bool = False
    ) -> HTMLResponse:
        parser = self.parse_map(logistics_subtype, is_collection)
        return HTMLResponse(self.gateway.cvs_map(data=parser))

    def parse_map(
        self, logistics_subtype: CvsMapSubTypeOptions, is_collection: bool = False
    ) -> EcpayCVSMapModel:

        return EcpayCVSMapModel(
            LogisticsType="CVS",
            LogisticsSubType=logistics_subtype,
            IsCollection="Y" if is_collection else "N",
            ServerReplyURL=self.server_reply_url,
        )


def get_logistics_map_method(
    provider: str = "ecpay", prefix_path: str = "logistics/map", state: str = ""
) -> EcpayLogisticsMap:
    if provider == "ecpay":
        return EcpayLogisticsMap(
            callback_url=f"{SdkConfig.api_host}/{prefix_path}/callback?state={state}"
        )
    raise ValueError("unrecognize logistics provider")


def get_logistics_create_method(
    provider: str = "ecpay",
    prefix_path: str = "logistics",
) -> Union[EcpayLogisticsCreate, SFLogisticsCreate]:
    if provider == "ecpay":
        return EcpayLogisticsCreate(
            callback_url=f"{SdkConfig.api_host}/{prefix_path}/{provider}/callback",
        )
    elif provider == "sf":
        return SFLogisticsCreate()
    raise ValueError("unrecognize logistics provider")


def get_callback_method(provider: str = "ecpay") -> EcpayLogisticsCallback:
    if provider == "ecpay":
        return EcpayLogisticsCallback()
    raise ValueError("unrecognize payment provider")


def get_logistics_status_method(provider: str = "sf") -> SFLogisticsStatus:
    if provider == "sf":
        return SFLogisticsStatus()
    raise ValueError("unrecognize logistics provider")


def get_shipping_note_method(provider: str = "ecpay") -> EcpayGetShippingNote:
    if provider == "ecpay":
        return EcpayGetShippingNote()
    raise ValueError("unrecognize logistics provider")


stepfn = boto3.client("stepfunctions", "ap-northeast-1")


async def process_callback(provider: str, request: Request) -> Response:
    callback_method = get_callback_method(provider)
    data = await callback_method.parse_request(request)
    callback_result = callback_method(data)
    # to avoid step function name duplicate error
    stepfn_name = f"{callback_result.order_id}_{callback_result.logistics_status}"
    stepfn.start_execution(
        stateMachineArn=SdkConfig.logistics_stepfn_arn,
        name=timestamp_postfix(stepfn_name),
        input=callback_result.json(),
    )
    return callback_method.respond(order_id=callback_result.order_id)

from datetime import datetime
from typing import Any, Dict, Optional, Union
from uuid import uuid4

import boto3
from fastapi import Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from fastel.cart import Cart
from fastel.cart.datastructures import InvoiceTypes, PaymentSubTypes
from fastel.collections import get_collection, get_site_config
from fastel.config import SdkConfig
from fastel.payment.common.models.callback import CallbackModel
from fastel.payment.common.models.invoice import InvoiceIssueResp, InvoiceStatus
from fastel.payment.common.models.order import Checkout, Order
from fastel.payment.ecpay import (
    ECPAY_CALLBACK_SUBTYPE,
    generate_B2B_invoice_data,
    generate_B2C_invoice_data,
)
from fastel.payment.ecpay.gateway import Ecpay, EcpayInvoice
from fastel.payment.ecpay.models.checkout import (
    EcCallback,
    EcCheckoutModel,
    EcGetNoCallback,
)
from fastel.payment.linepay.gateway import LinePay
from fastel.payment.linepay.models.checkout import (
    LinePayCallbackModel,
    LinePayCheckoutModel,
    LinePayConfirmModel,
    LinePayConfirmResp,
    LinePayRequestResp,
)
from fastel.payment.neweb.gateway import NewebInvoice, Newebpay
from fastel.payment.neweb.models.callback import (
    CallbackMsg,
    EncryptedCallback,
    GetNumMsg,
)
from fastel.payment.neweb.models.checkout import CheckoutModel
from fastel.payment.neweb.models.invoice import IssueModel, IssueResp
from fastel.payment.utils import PaymentStatus, auto_order_number, parse_order_number
from fastel.utils import TW, default_timestamp, timestamp_postfix
from fastel.utils.requests import parse_formdata


# Neweb Helpers
class NewebpayCheckout:
    def __init__(self, callback_url: str, number_url: str, redirect_url: str) -> None:
        self.gateway = Newebpay(
            SdkConfig.neweb_merchant_id,
            SdkConfig.neweb_hash_key,
            SdkConfig.neweb_hash_iv,
            stage=SdkConfig.stage,
        )
        self.notify_url = callback_url
        self.customer_url = number_url
        self.return_url = redirect_url

    def __call__(self, cart: Cart, **kwargs: Any) -> HTMLResponse:
        checkout_model = self.parse_payload(cart, **kwargs)
        now = default_timestamp()
        checkout_ins = {
            "order_number": checkout_model.MerchantOrderNo,
            "created": now,
            "updated": now,
            "expired": now + 7 * 24 * 3600 * 1000,
            "attempt": 0,
            "resolved": False,
        }
        cart.to_checkout(**checkout_ins)
        return HTMLResponse(self.gateway.checkout_request(checkout_model))

    def parse_payload(self, cart: Cart, **kwargs: Any) -> CheckoutModel:
        type_map = {}
        if cart.payment_subtype == PaymentSubTypes.credit:
            type_map["CREDIT"] = 1
        elif cart.payment_subtype == PaymentSubTypes.atm:
            type_map["VACC"] = 1
        elif cart.payment_subtype == PaymentSubTypes.linepay:
            type_map["LINEPAY"] = 1
        elif cart.payment_subtype == PaymentSubTypes.cod:
            type_map["CVSCOM"] = 1

        return CheckoutModel(
            Amt=cart.total,
            ItemDesc=cart.items.items[0].name,
            MerchantOrderNo=auto_order_number(),
            Email=cart.buyer_email,
            NotifyURL=self.notify_url,
            CustomerURL=self.customer_url,
            ReturnURL=self.return_url,
            **type_map,
            **kwargs,
        )


class NewebpayResume:
    def __init__(self, callback_url: str, number_url: str, redirect_url: str) -> None:
        self.gateway = Newebpay(
            SdkConfig.neweb_merchant_id,
            SdkConfig.neweb_hash_key,
            SdkConfig.neweb_hash_iv,
            stage=SdkConfig.stage,
        )
        self.notify_url = callback_url
        self.customer_url = number_url
        self.return_url = redirect_url

    def __call__(self, checkout: Checkout, **kwargs: Any) -> HTMLResponse:
        checkout_model = self.parse_payload(checkout, **kwargs)
        return HTMLResponse(self.gateway.checkout_request(checkout_model))

    def parse_payload(self, checkout: Checkout, **kwargs: Any) -> CheckoutModel:
        type_map = {}
        if checkout.payment_subtype == PaymentSubTypes.credit:
            type_map["CREDIT"] = 1
        elif checkout.payment_subtype == PaymentSubTypes.atm:
            type_map["VACC"] = 1
        elif checkout.payment_subtype == PaymentSubTypes.linepay:
            type_map["LINEPAY"] = 1
        elif checkout.payment_subtype == PaymentSubTypes.cod:
            type_map["CVSCOM"] = 1

        get_collection("checkout").update_one(
            {"order_number": checkout.order_number}, {"$inc": {"attempt": 1}}
        )
        return CheckoutModel(
            Amt=checkout.total,
            ItemDesc=checkout.items[0].name,
            MerchantOrderNo=f"{checkout.order_number}_{checkout.attempt}",
            Email=checkout.buyer_email,
            NotifyURL=self.notify_url,
            CustomerURL=self.customer_url,
            ReturnURL=self.return_url,
            **type_map,
            **kwargs,
        )


class NewebpayCallback:
    def __init__(self) -> None:
        self.gateway = Newebpay(
            SdkConfig.neweb_merchant_id,
            SdkConfig.neweb_hash_key,
            SdkConfig.neweb_hash_iv,
            stage=SdkConfig.stage,
        )

    def __call__(self, data: Dict[str, Any]) -> CallbackModel:
        validated = self.validate(data)
        decrypted = self.gateway.decrypt_callback(validated)
        parsed = self.parse_payload(decrypted)
        return parsed

    async def parse_request(self, request: Request) -> Dict[str, Any]:
        data = await request.form()
        return parse_formdata(data)

    def validate(self, data: Dict[str, Any]) -> EncryptedCallback:
        return EncryptedCallback.validate(data)

    def parse_payload(self, decrypted: CallbackMsg) -> CallbackModel:
        if decrypted.Status == "SUCCESS":
            payment_status = PaymentStatus.SUCCESS
        else:
            payment_status = PaymentStatus.FAILURE

        result = decrypted.Result
        if result.PaymentType == "CREDIT":
            payment_subtype = PaymentSubTypes.credit
        elif result.PaymentType == "VACC":
            payment_subtype = PaymentSubTypes.atm
        elif result.PaymentType == "CVSCOM":
            payment_subtype = PaymentSubTypes.cod
        elif result.PaymentType == "BARCODE":
            payment_subtype = PaymentSubTypes.barcode
        elif result.PaymentType == "WEBATM":
            payment_subtype = PaymentSubTypes.webatm
        else:
            payment_subtype = PaymentSubTypes.unknown

        parsered_order_number = parse_order_number(decrypted.Result.MerchantOrderNo)
        return CallbackModel(
            payment_status=payment_status,
            order_id=parsered_order_number,
            payment_subtype=payment_subtype,
            payment_transaction_detail=result.dict(),
            total=result.Amt,
        )

    def respond(self, **kwargs: Any) -> Response:
        return Response(content="1")


class NewebpayGetNumber:
    def __init__(self) -> None:
        self.gateway = Newebpay(
            SdkConfig.neweb_merchant_id,
            SdkConfig.neweb_hash_key,
            SdkConfig.neweb_hash_iv,
            stage=SdkConfig.stage,
        )

    def __call__(self, data: Dict[str, Any]) -> CallbackModel:
        validated = self.validate(data)
        decrypted = self.gateway.decrypt_getnum(validated)
        parsed = self.parse_payload(decrypted)
        return parsed

    async def parse_request(self, request: Request) -> Dict[str, Any]:
        data = await request.form()
        return parse_formdata(data)

    def validate(self, data: Dict[str, Any]) -> EncryptedCallback:
        return EncryptedCallback.validate(data)

    def parse_payload(self, decrypted: GetNumMsg) -> CallbackModel:
        result = decrypted.Result
        if decrypted.Status == "SUCCESS":
            payment_status = PaymentStatus.CODE_GENERATED
        else:
            payment_status = PaymentStatus.FAILURE

        expire_date = result.ExpireDate
        expire_time = result.ExpireTime

        if result.PaymentType == "VACC":
            payment_subtype = PaymentSubTypes.atm
        elif result.PaymentType == "BARCODE":
            payment_subtype = PaymentSubTypes.barcode
        elif result.PaymentType == "CVS":
            payment_subtype = PaymentSubTypes.cvs

        bank_code: Optional[str] = ""
        bank_account: Optional[str] = ""

        code_no: Optional[str] = ""

        barcode_1: Optional[str] = ""
        barcode_2: Optional[str] = ""
        barcode_3: Optional[str] = ""

        if payment_subtype == PaymentSubTypes.atm:
            bank_code = result.BankCode
            bank_account = result.CodeNo
        elif payment_subtype == PaymentSubTypes.cvs:
            code_no = result.CodeNo
        elif payment_subtype == PaymentSubTypes.barcode:
            barcode_1 = result.Barcode_1
            barcode_2 = result.Barcode_2
            barcode_3 = result.Barcode_3

        return CallbackModel(
            payment_status=payment_status,
            order_id=result.MerchantOrderNo,
            payment_redirect_detail=result.dict(exclude_none=True),
            total=result.Amt,
            pay_deadline=f"{expire_date} {expire_time}",
            payment_subtype=payment_subtype,
            bank_code=bank_code,
            bank_account=bank_account,
            code_no=code_no,
            barcode_1=barcode_1,
            barcode_2=barcode_2,
            barcode_3=barcode_3,
        )

    def respond(self, **kwargs: Any) -> Response:
        order_id = kwargs["order_id"]
        return RedirectResponse(
            url=f"{SdkConfig.web_host}/profile/orders?action=detail&is_created=true&order_number={order_id}",
            status_code=302,
        )


class NewebInvoiceIssue:
    def __init__(self) -> None:
        self.gateway = NewebInvoice(
            merchant_id=SdkConfig.neweb_invoice_merchant_id,
            hash_key=SdkConfig.neweb_invoice_hash_key,
            hash_iv=SdkConfig.neweb_invoice_hash_iv,
            stage=SdkConfig.stage,
        )

    def __call__(self, order: Dict[str, Any]) -> InvoiceIssueResp:
        validated = self.validate(order)
        parsed = self.parse_order(validated)
        gateway_resp = self.gateway.issue(parsed)
        return self.parse_gateway_resp(gateway_resp)

    def parse_gateway_resp(self, gateway_resp: IssueResp) -> InvoiceIssueResp:
        if gateway_resp.Status == "SUCCESS":
            status = InvoiceStatus.success
        else:
            status = InvoiceStatus.failure

        if gateway_resp.Result:
            invoice_number = gateway_resp.Result.InvoiceNumber
            invoice_random_no = gateway_resp.Result.RandomNum
        else:
            invoice_number = ""
            invoice_random_no = ""

        return InvoiceIssueResp(
            status=status,
            invoice_message=gateway_resp.Message,
            invoice_number=invoice_number,
            invoice_detail=gateway_resp.dict(),
            invoice_random_no=invoice_random_no,
        )

    def validate(self, order: Dict[str, Any]) -> Order:
        return Order.validate(order)

    def parse_order(self, order: Order) -> IssueModel:
        # items = order.items + order.extra_items + order.discount_items
        item_name = "|".join(list(map(lambda item: item.name, order.items)))
        item_count = "|".join(list(map(lambda item: str(item.config.qty), order.items)))
        item_unit = "|".join(list(map(lambda item: "個", order.items)))
        _amount = ""
        _price = ""
        for extra_item in order.extra_items:
            item_name += "|" + extra_item.get("name", "")
            item_count += "|1"
            item_unit += "|個"
            if order.invoice_type == InvoiceTypes.B2B:
                _amount += "|" + str(round(extra_item.get("amount", 0) / 1.05, 2))
                _price += "|" + str(round(extra_item.get("amount", 0) / 1.05, 2))
            else:
                _amount += "|" + str(extra_item.get("amount", 0))
                _price += "|" + str(extra_item.get("amount", 0))
        for discount_item in order.discount_items:
            item_name += "|" + discount_item.get("name", "")
            item_count += "|1"
            item_unit += "|個"
            if order.invoice_type == InvoiceTypes.B2B:
                _amount += "|-" + str(round(discount_item.get("sale_amount", 0), 2))
                _price += "|-" + str(round(discount_item.get("sale_amount", 0), 2))
            else:
                _amount += "|-" + str(discount_item.get("amount", 0))
                _price += "|-" + str(discount_item.get("amount", 0))
        if order.invoice_type == InvoiceTypes.B2B:
            item_amount = "|".join(
                list(map(lambda item: str(round(item.sales_amount)), order.items))
            )
            item_price = "|".join(
                list(map(lambda item: str(round(item.unit_sales)), order.items))
            )
        else:
            item_amount = "|".join(
                list(map(lambda item: str(item.amount), order.items))
            )
            item_price = "|".join(list(map(lambda item: str(item.price), order.items)))
        item_amount += _amount
        item_price += _price
        payload: Dict[str, Any] = {"BuyerName": order.buyer_name}

        if order.invoice_type == InvoiceTypes.B2B:
            payload["Category"] = "B2B"
            payload["BuyerUBN"] = order.b2b_company_no
            payload["BuyerName"] = order.b2b_company_name
            payload["PrintFlag"] = "Y"

        elif order.invoice_type == InvoiceTypes.B2C_DONATE:
            payload["Category"] = "B2C"
            payload["LoveCode"] = order.b2c_donate_code
            payload["PrintFlag"] = "N"

        elif order.invoice_type == InvoiceTypes.B2C_PHONE_CARRIER:
            payload["Category"] = "B2C"
            payload["CarrierType"] = "0"
            payload["CarrierNum"] = order.b2c_phone_carrier_code
            payload["PrintFlag"] = "N"

        elif order.invoice_type == InvoiceTypes.B2C_NPC:
            payload["Category"] = "B2C"
            payload["CarrierType"] = "1"
            payload["CarrierNum"] = order.b2c_npc_code
            payload["PrintFlag"] = "N"

        elif order.invoice_type == InvoiceTypes.B2C_PROVIDER:
            payload["Category"] = "B2C"
            payload["CarrierType"] = "2"
            payload["CarrierNum"] = order.buyer_email
            payload["PrintFlag"] = "N"

        elif order.invoice_type == InvoiceTypes.B2C:
            payload["Category"] = "B2C"
            payload["PrintFlag"] = "Y"

        return IssueModel(
            Status="1",
            MerchantOrderNo=auto_order_number(),
            Amt=order.sales,
            TaxAmt=order.tax,
            TotalAmt=order.total,
            TaxRate="5",
            TaxType="1",
            ItemName=item_name,
            ItemCount=item_count,
            ItemUnit=item_unit,
            ItemPrice=item_price,
            ItemAmt=item_amount,
            BuyerEmail=order.buyer_email,
            **payload,
        )


# Ecpay Helpers
class EcpayCheckout:
    def __init__(self, callback_url: str, number_url: str, redirect_url: str) -> None:
        self.gateway = Ecpay(
            SdkConfig.ecpay_merchant_id,
            SdkConfig.ecpay_hash_key,
            SdkConfig.ecpay_hash_iv,
            stage=SdkConfig.stage,
        )
        self.return_url = callback_url
        self.payment_info_url = number_url
        self.order_result_url = redirect_url

    def __call__(self, cart: Cart, **kwargs: Any) -> HTMLResponse:
        checkout_model = self.parse_payload(cart, **kwargs)
        now = default_timestamp()
        checkout_ins = {
            "order_number": checkout_model.MerchantTradeNo,
            "created": now,
            "updated": now,
            "expired": now + 7 * 24 * 3600 * 1000,
            "attempt": 0,
            "resolved": False,
        }
        cart.to_checkout(**checkout_ins)
        return HTMLResponse(self.gateway.checkout_request(checkout_model))

    @staticmethod
    def _replace_limit_name(name: str, limit: int) -> str:
        if len(name) > limit:
            return name[: limit - 3] + "..."
        return name

    def parse_payload(self, cart: Cart, **kwargs: Any) -> EcCheckoutModel:
        now = datetime.now(TW)
        type_map = {}
        if cart.payment_subtype == PaymentSubTypes.credit:
            type_map["ChoosePayment"] = "Credit"
            type_map["OrderResultURL"] = self.order_result_url
        elif cart.payment_subtype == PaymentSubTypes.webatm:
            type_map["ChoosePayment"] = "WebATM"
            type_map["OrderResultURL"] = self.order_result_url
        elif cart.payment_subtype == PaymentSubTypes.atm:
            type_map["ChoosePayment"] = "ATM"
            type_map["PaymentInfoURL"] = self.payment_info_url
            type_map["ClientRedirectURL"] = self.order_result_url
        elif cart.payment_subtype == PaymentSubTypes.cvs:
            type_map["ChoosePayment"] = "CVS"
            type_map["PaymentInfoURL"] = self.payment_info_url
            type_map["ClientRedirectURL"] = self.order_result_url
        elif cart.payment_subtype == PaymentSubTypes.barcode:
            type_map["ChoosePayment"] = "BARCODE"
            type_map["PaymentInfoURL"] = self.payment_info_url
            type_map["ClientRedirectURL"] = self.order_result_url
        elif cart.payment_subtype == PaymentSubTypes.default:
            type_map["ChoosePayment"] = "ALL"
            type_map["PaymentInfoURL"] = self.payment_info_url
            type_map["ClientRedirectURL"] = self.order_result_url
            type_map["OrderResultURL"] = self.order_result_url
        else:
            raise ValueError("invalid Payment Subtypes")

        name = "#".join([item.name for item in cart.items.items])
        item_name = self._replace_limit_name(name=name, limit=400)

        return EcCheckoutModel(
            TotalAmount=cart.total,
            ItemName=item_name,
            MerchantTradeNo=auto_order_number(),
            MerchantTradeDate=now.strftime("%Y/%m/%d %H:%M:%S"),
            ReturnURL=self.return_url,
            **type_map,
            **kwargs,
        )


class EcpayResume:
    def __init__(self, callback_url: str, number_url: str, redirect_url: str) -> None:
        self.gateway = Ecpay(
            SdkConfig.ecpay_merchant_id,
            SdkConfig.ecpay_hash_key,
            SdkConfig.ecpay_hash_iv,
            stage=SdkConfig.stage,
        )
        self.return_url = callback_url
        self.payment_info_url = number_url
        self.order_result_url = redirect_url

    def __call__(self, checkout: Checkout, **kwargs: Any) -> HTMLResponse:
        checkout_model = self.parse_payload(checkout, **kwargs)
        return HTMLResponse(self.gateway.checkout_request(checkout_model))

    @staticmethod
    def _replace_limit_name(name: str, limit: int) -> str:
        if len(name) > limit:
            return name[: limit - 3] + "..."
        return name

    def parse_payload(self, checkout: Checkout, **kwargs: Any) -> EcCheckoutModel:
        now = datetime.now(TW)
        type_map = {}
        if checkout.payment_subtype == PaymentSubTypes.credit:
            type_map["ChoosePayment"] = "Credit"
            type_map["OrderResultURL"] = self.order_result_url
        elif checkout.payment_subtype == PaymentSubTypes.webatm:
            type_map["ChoosePayment"] = "WebATM"
            type_map["OrderResultURL"] = self.order_result_url
        elif checkout.payment_subtype == PaymentSubTypes.atm:
            type_map["ChoosePayment"] = "ATM"
            type_map["PaymentInfoURL"] = self.payment_info_url
            type_map["ClientRedirectURL"] = self.order_result_url
        elif checkout.payment_subtype == PaymentSubTypes.cvs:
            type_map["ChoosePayment"] = "CVS"
            type_map["PaymentInfoURL"] = self.payment_info_url
            type_map["ClientRedirectURL"] = self.order_result_url
        elif checkout.payment_subtype == PaymentSubTypes.barcode:
            type_map["ChoosePayment"] = "BARCODE"
            type_map["PaymentInfoURL"] = self.payment_info_url
            type_map["ClientRedirectURL"] = self.order_result_url
        elif checkout.payment_subtype == PaymentSubTypes.default:
            type_map["ChoosePayment"] = "ALL"
            type_map["PaymentInfoURL"] = self.payment_info_url
            type_map["ClientRedirectURL"] = self.order_result_url
            type_map["OrderResultURL"] = self.order_result_url
        else:
            raise ValueError("invalid Payment Subtypes")

        name = "#".join([item.name for item in checkout.items])
        item_name = self._replace_limit_name(name=name, limit=400)

        get_collection("checkout").update_one(
            {"order_number": checkout.order_number}, {"$inc": {"attempt": 1}}
        )

        return EcCheckoutModel(
            TotalAmount=checkout.total,
            ItemName=item_name,
            MerchantTradeNo=f"{checkout.order_number}_{checkout.attempt}",
            MerchantTradeDate=now.strftime("%Y/%m/%d %H:%M:%S"),
            ReturnURL=self.return_url,
            **type_map,
            **kwargs,
        )


class EcpayCallback:
    def __init__(self) -> None:
        self.gateway = Ecpay(
            SdkConfig.ecpay_merchant_id,
            SdkConfig.ecpay_hash_key,
            SdkConfig.ecpay_hash_iv,
            stage=SdkConfig.stage,
        )
        self.response = "0|NOPE"

    def __call__(self, data: Dict[str, Any]) -> CallbackModel:
        validated = self.validate(data)
        self.check_mac_data(data=validated)
        parsed = self.parse_payload(validated)
        return parsed

    async def parse_request(self, request: Request) -> Dict[str, Any]:
        data = await request.form()
        return parse_formdata(data)

    def validate(self, data: Dict[str, Any]) -> EcCallback:
        return EcCallback.validate(data)

    def check_mac_data(self, data: EcCallback) -> None:
        mac_value = data.CheckMacValue
        result_data = data.dict(exclude_none=True)
        result_data.pop("CheckMacValue", None)

        result = self.gateway.cryptor.encrypt(result_data)
        if result == mac_value:
            self.response = "1|OK"

    def parse_payload(self, result: EcCallback) -> CallbackModel:
        if result.RtnCode == "1":
            payment_status = PaymentStatus.SUCCESS
        else:
            payment_status = PaymentStatus.FAILURE

        payment_type = result.PaymentType.split("_")[0]

        parsered_order_number = parse_order_number(result.MerchantTradeNo)

        return CallbackModel(
            payment_status=payment_status,
            order_id=parsered_order_number,
            total=result.TradeAmt,
            payment_subtype=ECPAY_CALLBACK_SUBTYPE[payment_type],
            payment_transaction_id=result.TradeNo,
            payment_transaction_time=result.PaymentDate,
            payment_transaction_detail=result.dict(exclude_none=True),
        )

    def respond(self, **kwargs: Any) -> Response:
        return Response(content=self.response)


class EcpayGetNumber:
    def __init__(self) -> None:
        self.gateway = Ecpay(
            SdkConfig.neweb_merchant_id,
            SdkConfig.neweb_hash_key,
            SdkConfig.neweb_hash_iv,
            stage=SdkConfig.stage,
        )
        self.response = "0|NOPE"

    def __call__(self, data: Dict[str, Any]) -> CallbackModel:
        validated = self.validate(data)
        self.check_mac_data(data=validated)
        parsed = self.parse_payload(validated)
        return parsed

    async def parse_request(self, request: Request) -> Dict[str, Any]:
        data = await request.form()
        return parse_formdata(data)

    def validate(self, data: Dict[str, Any]) -> EcGetNoCallback:
        return EcGetNoCallback.validate(data)

    def check_mac_data(self, data: EcGetNoCallback) -> None:
        mac_value = data.CheckMacValue
        result_data = data.dict(exclude_none=True)
        result_data.pop("CheckMacValue", None)

        if data.PaymentType.startswith("CVS"):
            result_data.pop("BankCode", None)
            result_data.pop("vAccount", None)
        else:
            result_data.pop("Barcode1")
            result_data.pop("Barcode2")
            result_data.pop("Barcode3")
            result_data.pop("PaymentNo", None)

        result = self.gateway.cryptor.encrypt(result_data)
        if result == mac_value:
            self.response = "1|OK"

    def parse_payload(self, result: EcGetNoCallback) -> CallbackModel:
        if result.RtnCode in ["2", "10100073"]:
            payment_status = PaymentStatus.CODE_GENERATED
        else:
            payment_status = PaymentStatus.FAILURE

        result_payment_type = result.PaymentType.split("_")[0]

        bank_code: Optional[str] = ""
        bank_account: Optional[str] = ""

        code_no: Optional[str] = ""

        barcode_1: Optional[str] = ""
        barcode_2: Optional[str] = ""
        barcode_3: Optional[str] = ""

        if result_payment_type == "ATM":
            bank_code = result.BankCode
            bank_account = result.vAccount
        elif result_payment_type == "BARCODE":
            barcode_1 = result.Barcode1
            barcode_2 = result.Barcode2
            barcode_3 = result.Barcode3
        elif result_payment_type == "CVS":
            code_no = result.PaymentNo

        return CallbackModel(
            payment_status=payment_status,
            order_id=result.MerchantTradeNo,
            total=result.TradeAmt,
            pay_deadline=result.ExpireDate,
            payment_subtype=ECPAY_CALLBACK_SUBTYPE[result_payment_type],
            payment_transaction_id=result.TradeNo,
            payment_transaction_time=result.TradeDate,
            payment_redirect_detail=result.dict(exclude_none=True),
            bank_code=bank_code,
            bank_account=bank_account,
            code_no=code_no,
            barcode_1=barcode_1,
            barcode_2=barcode_2,
            barcode_3=barcode_3,
        )

    def respond(self, **kwargs: Any) -> Response:
        return Response(content=self.response)


class EcpayInvoiceIssue:
    def __init__(self) -> None:
        self.gateway = EcpayInvoice(
            merchant_id=SdkConfig.ecpay_invoice_merchant_id,
            hash_key=SdkConfig.ecpay_invoice_hash_key,
            hash_iv=SdkConfig.ecpay_invoice_hash_iv,
            stage=SdkConfig.stage,
        )

    def __call__(self, order: Dict[str, Any]) -> InvoiceIssueResp:
        validated = self.validate(order)
        parsed = self.parse_order(validated)
        gateway_resp = self.gateway.issue(parsed)
        result = self.parse_gateway_resp(gateway_resp=gateway_resp)
        return result

    def validate(self, order: Dict[str, Any]) -> Order:
        return Order.validate(order)

    def parse_order(self, order: Order) -> Dict[str, Any]:
        if order.invoice_type == InvoiceTypes.B2B:
            payload = generate_B2B_invoice_data(order=order.dict())
        else:
            payload = generate_B2C_invoice_data(order=order.dict())
        payload["MerchantID"] = SdkConfig.ecpay_invoice_merchant_id

        return payload

    def parse_gateway_resp(self, gateway_resp: Dict[str, Any]) -> InvoiceIssueResp:
        resp_data = gateway_resp.get("Data", {})
        if resp_data["RtnCode"] == 1:
            status = InvoiceStatus.success
            invoice_number = resp_data.get("InvoiceNumber", "") or resp_data.get(
                "InvoiceNo", ""
            )
        else:
            status = InvoiceStatus.failure
            invoice_number = ""

        return InvoiceIssueResp(
            status=status,
            invoice_message=resp_data.get("RtnMsg", ""),
            invoice_number=invoice_number,
            invoice_detail=gateway_resp,
            invoice_random_no=resp_data.get("RandomNumber", ""),
        )


class LinePayCheckout:
    def __init__(self, callback_url: str, error_url: str) -> None:
        self.gateway = LinePay(
            SdkConfig.linepay_channel_id,
            SdkConfig.linepay_channel_secret,
            stage=SdkConfig.stage,
        )
        self.callback_url = callback_url
        self.error_url = error_url

    def __call__(self, cart: Cart, **kwargs: Any) -> Response:
        checkout_model = self.parse_payload(cart, **kwargs)
        checkout_resp = self.gateway.checkout_request(checkout_model)
        response = self.parse_gateway_resp(checkout_resp)
        now = default_timestamp()
        checkout_ins = {
            "order_number": checkout_model.orderId,
            "created": now,
            "updated": now,
            "expired": now + 7 * 24 * 3600 * 1000,
            "attempt": 0,
            "resolved": False,
        }
        cart.to_checkout(**checkout_ins)
        return response

    def parse_gateway_resp(self, gateway_resp: LinePayRequestResp) -> Response:
        if gateway_resp.returnCode == "0000" and gateway_resp.info:
            redirect_url = gateway_resp.info.paymentUrl.web
        else:
            redirect_url = self.error_url

        return RedirectResponse(url=redirect_url, status_code=302)

    def parse_payload(self, cart: Cart, **kwargs: Any) -> LinePayCheckoutModel:
        if cart.payment_subtype != PaymentSubTypes.linepay:
            raise ValueError("payment_subtype should be linepay")

        first_item = cart.items.items[0].to_dict()
        name = first_item["name"] + "與其他商品."
        checkout_products = [
            {
                "id": uuid4().__str__(),
                "amount": cart.total,
                "products": [
                    {
                        "id": uuid4().__str__(),
                        "name": name,
                        "imageUrl": first_item["product"]["images"][0]["expected_url"],
                        "quantity": 1,
                        "price": cart.total,
                    }
                ],
            }
        ]
        return LinePayCheckoutModel(
            amount=cart.total,
            currency="TWD",
            orderId=auto_order_number(),
            packages=checkout_products,
            redirectUrls={
                "confirmUrl": self.callback_url,
                "cancelUrl": self.callback_url,
            },
        )


class LinePayCallback:
    def __init__(self) -> None:
        self.gateway = LinePay(
            SdkConfig.linepay_channel_id,
            SdkConfig.linepay_channel_secret,
            stage=SdkConfig.stage,
        )

    def __call__(self, data: Dict[str, Any]) -> CallbackModel:
        callback_model = self.validate(data)
        confirm_model = self.build_confirm_model(callback_model)
        gateway_resp = self.gateway.checkout_confirm(confirm_model)
        return self.parse_gateway_resp(gateway_resp)

    def validate(self, data: Dict[str, Any]) -> LinePayCallbackModel:
        return LinePayCallbackModel.validate(data)

    def build_confirm_model(
        self,
        callback_model: LinePayCallbackModel,
    ) -> LinePayConfirmModel:
        checkout_dict = get_collection("checkout").find_one(
            {"order_number": callback_model.orderId}
        )
        return LinePayConfirmModel(
            amount=checkout_dict["total"], transactionId=callback_model.transactionId
        )

    async def parse_request(self, request: Request) -> Dict[str, Any]:
        data: Dict[str, Any] = request.query_params._dict
        return data

    def parse_gateway_resp(self, gateway_resp: LinePayConfirmResp) -> CallbackModel:
        if gateway_resp.returnCode == "0000" and gateway_resp.info:
            payment_status = PaymentStatus.SUCCESS
            total = gateway_resp.info.payInfo[0]["amount"]  # type: ignore
            payment_transaction_id = gateway_resp.info.transactionId
            order_id = gateway_resp.info.orderId
        else:
            payment_status = PaymentStatus.FAILURE
            total = 0
            payment_transaction_id = "error"
            order_id = "error"
        return CallbackModel(
            payment_subtype=PaymentSubTypes.linepay,
            payment_status=payment_status,
            payment_transaction_id=payment_transaction_id,
            payment_transaction_detail=gateway_resp.info,
            total=total,
            order_id=order_id,
        )

    def respond(self, **kwargs: Any) -> Response:
        order_id = kwargs["order_id"]
        return RedirectResponse(
            url=f"{SdkConfig.web_host}/profile/orders?action=detail&is_created=true&order_number={order_id}",
            status_code=302,
        )


def get_resume_method(
    prefix_path: str = "payment",
) -> Union[NewebpayResume, EcpayResume]:
    default_payment_provider = get_site_config("default_payment_provider", "ecpay")
    if default_payment_provider == "neweb":
        return NewebpayResume(
            callback_url=f"{SdkConfig.api_host}/{prefix_path}/callback",
            number_url=f"{SdkConfig.api_host}/{prefix_path}/number",
            redirect_url=f"{SdkConfig.api_host}/{prefix_path}/return",
        )
    elif default_payment_provider == "ecpay":
        return EcpayResume(
            callback_url=f"{SdkConfig.api_host}/{prefix_path}/callback",
            number_url=f"{SdkConfig.api_host}/{prefix_path}/number",
            redirect_url=f"{SdkConfig.api_host}/{prefix_path}/return",
        )

    raise ValueError("unrecognize payment provider")


def get_checkout_method(
    prefix_path: str = "payment",
) -> Union[NewebpayCheckout, EcpayCheckout, LinePayCheckout]:
    default_payment_provider = get_site_config("default_payment_provider", "ecpay")
    if default_payment_provider == "neweb":
        return NewebpayCheckout(
            callback_url=f"{SdkConfig.api_host}/{prefix_path}/callback",
            number_url=f"{SdkConfig.api_host}/{prefix_path}/number",
            redirect_url=f"{SdkConfig.api_host}/{prefix_path}/return",
        )
    elif default_payment_provider == "ecpay":
        return EcpayCheckout(
            callback_url=f"{SdkConfig.api_host}/{prefix_path}/callback",
            number_url=f"{SdkConfig.api_host}/{prefix_path}/number",
            redirect_url=f"{SdkConfig.api_host}/{prefix_path}/return",
        )
    elif default_payment_provider == "linepay":
        return LinePayCheckout(
            callback_url=f"{SdkConfig.api_host}/{prefix_path}/callback",
            error_url=f"{SdkConfig.web_host}/misc/error?title=結帳發生錯誤&url={SdkConfig.web_host}&btn_text=返回首頁",
        )

    raise ValueError("unrecognize payment provider")


def get_callback_method() -> Union[NewebpayCallback, EcpayCallback, LinePayCallback]:
    default_payment_provider = get_site_config("default_payment_provider", "ecpay")
    if default_payment_provider == "neweb":
        return NewebpayCallback()
    elif default_payment_provider == "ecpay":
        return EcpayCallback()
    elif default_payment_provider == "linepay":
        return LinePayCallback()
    raise ValueError("unrecognize payment provider")


def get_getnum_method() -> Union[NewebpayGetNumber, EcpayGetNumber]:
    default_payment_provider = get_site_config("default_payment_provider", "ecpay")
    if default_payment_provider == "neweb":
        return NewebpayGetNumber()
    elif default_payment_provider == "ecpay":
        return EcpayGetNumber()
    raise ValueError("unrecognize payment provider")


def get_invoice_issue_method() -> Union[NewebInvoiceIssue, EcpayInvoiceIssue]:
    default_payment_provider = get_site_config("default_payment_provider", "ecpay")
    if default_payment_provider == "neweb":
        return NewebInvoiceIssue()
    elif default_payment_provider == "ecpay":
        return EcpayInvoiceIssue()
    raise ValueError("unrecognize payment provider")


stepfn = boto3.client("stepfunctions", "ap-northeast-1")


async def process_callback(request: Request) -> Response:
    callback_method = get_callback_method()
    data = await callback_method.parse_request(request)
    callback_result = callback_method(data)
    stepfn_name = (
        f"callback_{callback_result.order_id}_{callback_result.payment_status}"
    )
    stepfn.start_execution(
        stateMachineArn=SdkConfig.payment_stepfn_arn,
        name=timestamp_postfix(stepfn_name),
        input=callback_result.json(),
    )

    return callback_method.respond(order_id=callback_result.order_id)


async def process_redirect(request: Request) -> Response:
    callback_method = get_callback_method()
    data = await callback_method.parse_request(request)
    callback_result = callback_method(data)
    return RedirectResponse(
        url=f"{SdkConfig.web_host}/profile/orders?action=detail&is_created=true&order_number={callback_result.order_id}",
        status_code=302,
    )


async def process_getnum(request: Request) -> Response:
    getnum_method = get_getnum_method()
    data = await getnum_method.parse_request(request)
    getnum_result = getnum_method(data)
    stepfn_name = f"getnum_{getnum_result.order_id}_{getnum_result.payment_status}"
    stepfn.start_execution(
        stateMachineArn=SdkConfig.payment_stepfn_arn,
        name=timestamp_postfix(stepfn_name),
        input=getnum_result.json(),
    )

    return getnum_method.respond(order_id=getnum_result.order_id)


def process_invoice_issue(order: Dict[str, Any]) -> InvoiceIssueResp:
    issue_method = get_invoice_issue_method()
    issue_resp = issue_method(order)

    return issue_resp

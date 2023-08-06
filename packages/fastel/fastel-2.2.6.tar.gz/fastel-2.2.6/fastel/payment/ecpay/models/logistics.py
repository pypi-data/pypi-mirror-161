import time
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, EmailStr

CvsMapSubTypeOptions = Literal[
    "FAMI", "UNIMART", "FAMIC2C", "UNIMARTC2C", "HILIFE", "HILIFEC2C", "OKMARTC2C"
]

LogisticsTypeOptions = Literal["CVS", "Home"]
LogisticsStatusOptions = Literal[
    "pending",
    "in_delivery",
    "delivered",
    "exception",
    "center_delivered",
    "store_delivered",
]

LogisticSubTypeOptions = Literal[
    "FAMI",
    "UNIMART",
    "HILIFE",
    "FAMIC2C",
    "UNIMARTC2C",
    "HILIFEC2C",
    "OKMARTC2C",
    "TCAT",
    "ECAN",
]

DistanceOptions = Literal["00", "01", "02"]
TemperatureOptions = Literal["0001", "0002", "0003"]
SpecificationOptions = Literal["0001", "0002", "0003", "0004"]
ScheduledPickupTimeOptions = Literal["1", "2", "3", "4"]
ScheduledDeliveryTimeOptions = Literal["1", "2", "3", "4", "12", "13", "23"]


class CVSMapModel(BaseModel):
    LogisticsType: Literal["CVS"] = "CVS"
    LogisticsSubType: CvsMapSubTypeOptions = "FAMI"
    IsCollection: Literal["Y", "N"]
    Device: int = 0
    redirect_url: Optional[str]


class LogisticModel(BaseModel):
    MerchantTradeNo: str
    LogisticsType: LogisticsTypeOptions = "Home"
    LogisticsSubType: LogisticSubTypeOptions = "TCAT"
    GoodsName: Optional[str]
    GoodsAmount: int
    SenderName: str
    SenderPhone: str
    SenderCellPhone: Optional[str]
    ReceiverName: str
    ReceiverCellPhone: str
    ReceiverEmail: EmailStr
    IsCollection: Optional[bool]
    CollectionAmount: Optional[int]
    ReceiverStoreID: Optional[str]
    TradeDesc: Optional[str]
    Remark: Optional[str]

    # if LogisticsType = Home
    Distance: Optional[DistanceOptions]
    Temperature: Optional[TemperatureOptions]
    Specification: Optional[SpecificationOptions]
    ScheduledPickupTime: Optional[ScheduledPickupTimeOptions]
    ScheduledDeliveryTime: Optional[ScheduledDeliveryTimeOptions]
    ScheduledDeliveryDate: Optional[str]
    PackageCount: Optional[int]
    SenderZipCode: Optional[str]
    SenderAddress: Optional[str]
    ReceiverZipCode: Optional[str]
    ReceiverAddress: Optional[str]

    # only C2C
    ReturnStoreID: Optional[str]
    LogisticsC2CReplyURL: Optional[str]


class CallbackModel(BaseModel):
    logistics_status: LogisticsStatusOptions = "pending"
    logistics_type: str
    logistics_subtype: str
    logistics_id: str
    detail: Dict[str, Any]

    @property
    def rtn_random(self) -> str:
        rtn_code = self.detail.get("RtnCode", "ERR")
        return f"{rtn_code}_{int(time.time())}"

    @property
    def stepfn_name(self) -> str:
        return f"{self.logistics_id}_{self.logistics_status}_{self.rtn_random}"


class LogisticsDetailModel(BaseModel):
    MerchantID: str
    MerchantTradeNo: str
    RtnCode: str
    RtnMsg: str
    AllPayLogisticsID: str
    LogisticsType: str
    LogisticsSubType: Literal[
        "FAMIC2C",
        "UNIMARTC2C",
        "HILIFEC2C",
        "OKMARTC2C",
        "FAMI",
        "UNIMART",
        "UNIMARTFREEZE",
        "HILIFE",
        "TCAT",
        "ECAN",
    ]
    GoodsAmount: int
    UpdateStatusDate: str
    ReceiverName: str
    ReceiverPhone: str
    ReceiverCellPhone: str
    ReceiverEmail: str
    ReceiverAddress: str
    CVSPaymentNo: str
    CVSValidationNo: str
    BookingNote: str
    CheckMacValue: str


class LogisticsDataModel(BaseModel):
    trade_no: str
    logistics_id: str
    logistics_type: str
    logistics_sub_type: Literal[
        "FAMIC2C",
        "UNIMARTC2C",
        "HILIFEC2C",
        "OKMARTC2C",
        "FAMI",
        "UNIMART",
        "UNIMARTFREEZE",
        "HILIFE",
        "TCAT",
        "ECAN",
    ]
    cvs_payment_no: str
    cvs_validation_no: str
    goods_amount: int
    update_status_date: str
    rtn_code: str
    rtn_msg: str
    receiver_name: str
    receiver_phone: str
    receiver_cell_phone: str
    receiver_email: str
    receiver_address: str

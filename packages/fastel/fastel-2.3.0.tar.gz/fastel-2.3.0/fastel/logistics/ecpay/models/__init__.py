from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, EmailStr, validator

LogisticsTypeOptions = Literal["CVS", "Home"]

LogisticsSubTypeOptions = Literal[
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
LogisticsStatusOptions = Literal[
    "pending",
    "in_delivery",
    "delivered",
    "exception",
    "center_delivered",
    "store_delivered",
]

DistanceOptions = Literal["00", "01", "02"]
TemperatureOptions = Literal["0001", "0002", "0003"]
SpecificationOptions = Literal["0001", "0002", "0003", "0004"]
ScheduledPickupTimeOptions = Literal["1", "2", "3", "4"]
ScheduledDeliveryTimeOptions = Literal["1", "2", "3", "4", "12", "13", "23"]

CvsMapSubTypeOptions = Literal[
    "FAMI", "UNIMART", "FAMIC2C", "UNIMARTC2C", "HILIFE", "HILIFEC2C", "OKMARTC2C"
]


class EcpayLogisticsModel(BaseModel):
    MerchantTradeNo: str
    LogisticsType: LogisticsTypeOptions = "Home"
    LogisticsSubType: LogisticsSubTypeOptions = "TCAT"
    GoodsName: Optional[str]
    GoodsAmount: int
    SenderName: str
    SenderPhone: str
    SenderCellPhone: Optional[str]
    ReceiverName: str
    ReceiverCellPhone: str
    ReceiverEmail: EmailStr
    IsCollection: Literal["Y", "N"] = "N"
    CollectionAmount: Optional[int]
    ReceiverStoreID: Optional[str]
    TradeDesc: Optional[str]
    Remark: Optional[str]
    ServerReplyURL: str

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


class LogisticsTypes(str, Enum):
    HOME = "HOME"
    CVS = "CVS"


class EcpayLogisticsCallbackModel(BaseModel):
    MerchantID: str
    MerchantTradeNo: str
    RtnCode: str
    RtnMsg: str
    AllPayLogisticsID: str
    LogisticsType: LogisticsTypes
    LogisticsSubType: str
    GoodsAmount: int
    UpdateStatusDate: str = ""
    ReceiverName: str = ""
    ReceiverPhone: str = ""
    ReceiverCellPhone: str = ""
    ReceiverEmail: str = ""
    ReceiverAddress: str = ""
    CVSPaymentNo: str = ""
    CVSValidationNo: str = ""
    BookingNote: str = ""
    CheckMacValue: str

    @validator("RtnMsg", "ReceiverAddress", "ReceiverName")
    def validate_msg(cls, v: str, **kwargs: Any) -> str:
        return v.encode("Latin-1").decode()


class CVSSubtypes(str, Enum):
    FAMI = "FAMI"
    UNIMART = "UNIMART"
    HILIFE = "HILIFE"
    FAMIC2C = "FAMIC2C"
    UNIMARTC2C = "UNIMARTC2C"
    HILIFEC2C = "HILIFEC2C"
    OKMARTC2C = "OKMARTC2C"


class EcpayCVSMapModel(BaseModel):
    LogisticsType: Literal["CVS"] = "CVS"
    LogisticsSubType: CvsMapSubTypeOptions = "FAMI"
    IsCollection: Literal["Y", "N"]
    Device: int = 0
    ServerReplyURL: str


class CVSMapCallback(BaseModel):
    MerchantID: str = ""
    MerchantTradeNo: str = ""
    LogisticsSubType: str = ""
    CVSStoreID: str = ""
    CVSStoreName: str = ""
    CVSAddress: str = ""
    CVSTelephone: str = ""
    CVSOutSide: str = ""


class EcpayPrintOrderInfo(BaseModel):
    LogisticsSubType: Literal[
        "FAMIC2C",
        "UniMartC2C",
        "HILIFEC2C",
        "OKMARTC2C",
        "FAMI",
        "UNIMART",
        "UNIMARTFREEZE",
        "HILIFE",
        "TCAT",
        "ECAN",
    ]
    AllPayLogisticsID: str
    CVSPaymentNo: Optional[str]
    CVSValidationNo: Optional[str]

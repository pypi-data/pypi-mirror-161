from typing import List, Literal, Optional

from pydantic import BaseModel

PLATFORM_CODE = Literal[
    "INT0053",
    "INT0054",
    "INT0257",
    "INT0451",
    "INT0391",
    "INT0392",
    "INT0399",
    "INT0400",
    "INT0263",
    "INT0007",
    "INT0008",
    "INT0137",
    "INT0139",
    "INT0013",
    "INT0014",
    "INT0253",
    "INT0282",
    "INT0275",
    "INT0173",
    "INT0174",
    "INT0175",
    "INT0176",
    "INT0177",
    "INT0172",
    "INT0001",
    "INT0009",
    "INT0287",
    "INT0280",
    "INT0201",
    "INT0010",
    "INT0005",
    "INT0006",
    "INT0011",
    "INT0214",
    "INT0248",
]

COUNTRY = Literal[
    "CN",
    "HK",
    "TW",
    "MO",
    "AU",
    "BD",
    "IN",
    "ID",
    "JP",
    "KR",
    "MY",
    "NZ",
    "SG",
    "TH",
    "US",
    "VN",
    "AT",
    "BE",
    "BG",
]

CURRENCY = Literal[
    "USD",
    "CNY",
    "HKD",
    "EUR",
    "RUB",
    "NTD",
    "MOP",
    "SGD",
    "JPY",
    "KRW",
    "MYR",
    "VND",
    "THB",
    "AUD",
    "MNT",
]


class PaymentInfo(BaseModel):
    # 付款方式 1 寄方付， 2 收方付， 3 第三方付
    payMethod: Literal["1", "2", "3"] = "3"
    taxPayMethod: Literal["1", "2", "3"] = "3"
    payMonthCard: str


class BaseInfo(BaseModel):
    # 收/寄件人名字
    contact: str
    # 收/寄件國家/地區
    country: COUNTRY = "TW"
    # 郵編
    postCode: str
    # 州/省
    regionFirst: str = "台灣省"
    # 城市
    regionSecond: str = "台北市"
    # 區
    regionThird: str = "大同區"
    address: str
    email: str = ""
    cargoType: Literal[1, 2] = 1


class SenderInfo(BaseInfo):
    telNo: str = ""


class ReceiverInfo(BaseInfo):
    phoneNo: str = ""


class ParcelInfoList(BaseModel):
    name: str
    unit: str = "個"
    amount: float
    currency: CURRENCY = "NTD"
    quantity: float
    originCountry: COUNTRY = "TW"


class SFLogisticsModel(BaseModel):
    customerCode: str
    orderOperateType: Literal[1, 5]
    customerOrderNo: str
    interProductCode: PLATFORM_CODE = "INT0053"
    # 包裹數 *
    parcelQuantity: int = 1
    # 聲明價值 * order
    declaredValue: int
    # 包裹总计声明价值币种
    declaredCurrency: str = "NTD"
    # 寄件方式 0: 服務點自寄或自行聯繫快遞員 1: 上門收件
    pickupType: Literal["0", "1"] = "1"
    # 上門區間預約時間 yyyy-MM-dd HH:mm 如果pickupType 為 1 則必填
    pickupAppointTime: Optional[str]
    # 收件時區
    pickupAppointTimeZone: str = "Asia/Taipei"
    # 運單備註 *
    remark: str = ""
    # 付款方式
    paymentInfo: PaymentInfo
    # 寄件人訊息
    senderInfo: SenderInfo
    # 收件人訊息
    receiverInfo: ReceiverInfo
    # 包裹訊息
    parcelInfoList: List[ParcelInfoList]

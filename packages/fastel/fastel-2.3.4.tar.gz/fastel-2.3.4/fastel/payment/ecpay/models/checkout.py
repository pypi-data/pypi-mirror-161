from typing import Any, Literal, Optional

from pydantic import BaseModel, validator


class EcCheckoutModel(BaseModel):
    MerchantTradeNo: str
    TotalAmount: int
    ItemName: str = "Online Payment To Ecpay"
    TradeDesc: str = "no description"
    ChoosePayment: Literal["ALL", "Credit", "WebATM", "ATM", "CVS", "BARCODE"] = "ALL"
    BindingCard: Literal[0, 1] = 0
    MerchantMemberID: Optional[str]
    RelateNumber: Optional[str]
    PaymentType: str = "aio"
    InvoiceMark: Optional[Literal["Y", "N"]] = "N"
    # only fill this if InvoiceMark is Y
    TaxType: Optional[Literal["1", "2", "3", "9"]]
    ReturnURL: Optional[str]
    OrderResultURL: Optional[str]
    PaymentInfoURL: Optional[str]
    ClientRedirectURL: Optional[str]


class EcGetNoCallback(BaseModel):
    MerchantID: str = ""
    MerchantTradeNo: str = ""
    StoreID: str = ""
    RtnCode: str = ""
    RtnMsg: str = ""
    TradeNo: str = ""
    TradeAmt: int = 0
    PaymentType: str = ""
    TradeDate: Optional[str] = ""
    CheckMacValue: Optional[str] = ""
    BankCode: Optional[str] = ""  # 取號結果ATM
    vAccount: Optional[str] = ""  # 取號結果ATM
    ExpireDate: Optional[str] = ""  # 取號結果ATM、CVS和BARCODE
    PaymentNo: Optional[str] = ""  # 取號結果CVS和BARCODE
    Barcode1: Optional[str] = ""  # 取號結果CVS和BARCODE
    Barcode2: Optional[str] = ""  # 取號結果CVS和BARCODE
    Barcode3: Optional[str] = ""  # 取號結果CVS和BARCODE
    CustomField1: Optional[str] = ""
    CustomField2: Optional[str] = ""
    CustomField3: Optional[str] = ""
    CustomField4: Optional[str] = ""


class EcCallback(BaseModel):
    MerchantID: str
    MerchantTradeNo: str
    RtnCode: str
    RtnMsg: str
    TradeNo: str
    TradeAmt: int
    PaymentDate: Optional[str]
    PaymentType: str
    PaymentTypeChargeFee: Optional[int]
    TradeDate: str
    CheckMacValue: str
    StoreID: Optional[str] = ""
    SimulatePaid: Optional[int] = 0
    CustomField1: Optional[str] = ""
    CustomField2: Optional[str] = ""
    CustomField3: Optional[str] = ""
    CustomField4: Optional[str] = ""

    @validator("RtnMsg")
    def validate_msg(cls, v: str, values: Any, **kwargs: Any) -> str:
        return v.encode("Latin-1").decode()

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GetNumResult(BaseModel):
    MerchantID: str
    Amt: str
    TradeNo: str
    MerchantOrderNo: str
    PaymentType: str
    ExpireDate: Optional[str] = ""
    ExpireTime: Optional[str] = "00:00:00"

    BankCode: Optional[str]
    CodeNo: Optional[str]

    Barcode_1: Optional[str]
    Barcode_2: Optional[str]
    Barcode_3: Optional[str]


class Result(BaseModel):
    Amt: int
    MerchantID: str
    MerchantOrderNo: str
    PaymentType: str
    TradeNo: str
    EscrowBank: Optional[str] = None
    IP: Optional[str] = None
    PayTime: Optional[str] = None
    RespondType: Optional[str] = None
    ExpireDate: Optional[datetime] = None  # 取號回傳
    ExpireTime: Optional[datetime] = None  # 取號回傳
    AuthBank: Optional[str] = None  # 信用卡支付回傳參數
    RespondCode: Optional[str] = None  # 信用卡支付回傳參數
    Auth: Optional[str] = None  # 信用卡支付回傳參數
    Card4No: Optional[str] = None  # 信用卡支付回傳參數
    Card6No: Optional[str] = None  # 信用卡支付回傳參數
    Inst: Optional[int] = None  # 信用卡支付回傳參數
    InstEach: Optional[int] = None  # 信用卡支付回傳參數
    InstFirst: Optional[int] = None  # 信用卡支付回傳參數
    ECI: Optional[str] = None  # 信用卡支付回傳參數
    TokenUseStatus: Optional[str] = None  # 信用卡支付回傳參數
    RedAmt: Optional[int] = None  # 信用卡支付回傳參數
    PaymentMethod: Optional[str] = None  # 信用卡支付回傳參數
    DCC_Amt: Optional[float] = None  # 信用卡支付回傳參數
    DCC_Rate: Optional[float] = None  # 信用卡支付回傳參數
    DCC_Markup: Optional[float] = None  # 信用卡支付回傳參數
    DCC_Currency: Optional[str] = None  # 信用卡支付回傳參數
    DCC_Currency_Code: Optional[int] = None  # 信用卡支付回傳參數
    PayBankCode: Optional[str] = None  # WEBATM、ATM
    PayerAccount5Code: Optional[str] = None  # WEBATM、ATM
    CodeNo: Optional[str] = None  # 超商代碼 & ATM轉帳
    StoreType: Optional[int] = None  # 超商代碼 & 超商物流
    StoreID: Optional[str] = None  # 超商代碼
    Barcode_1: Optional[str] = None  # 超商條碼
    Barcode_2: Optional[str] = None  # 超商條碼
    Barcode_3: Optional[str] = None  # 超商條碼
    PayStore: Optional[str] = None  # 超商條碼
    P2GTradeNo: Optional[str] = None  # ezpay電子錢包
    P2GPaymentType: Optional[str] = None  # ezpay電子錢包
    P2GAmt: Optional[int] = None  # ezpay電子錢包
    StoreCode: Optional[str] = None  # 超商物流
    StoreName: Optional[str] = None  # 超商物流
    StoreAddr: Optional[str] = None  # 超商物流
    TradeType: Optional[int] = None  # 超商物流
    CVSCOMName: Optional[str] = None  # 超商物流
    CVSCOMPhone: Optional[str] = None  # 超商物流
    ChannelID: Optional[str] = None  # 跨境支付
    ChannelNo: Optional[str] = None  # 跨境支付
    BankCode: Optional[str] = None  # ATM轉帳


class CallbackMsg(BaseModel):
    Status: str
    Message: str
    Result: Result


class EncryptedCallback(BaseModel):
    Status: str
    MerchantID: str
    TradeInfo: str


class GetNumMsg(BaseModel):
    Status: str
    Message: str
    Result: GetNumResult

from typing import Literal, Optional

from pydantic import BaseModel


class EZItem(BaseModel):
    name: str
    quantity: float
    price: float
    amount: float
    unit: str = "個"


class IssueModel(BaseModel):
    TransNum: Optional[str]
    MerchantOrderNo: str
    Status: Literal["0", "1", "3"] = "1"
    CreateStatusTime: Optional[str]
    Category: Literal["B2B", "B2C"] = "B2C"
    BuyerName: str
    BuyerUBN: Optional[str]
    BuyerAddress: Optional[str]
    BuyerEmail: Optional[str]
    ItemName: str
    ItemUnit: str
    ItemPrice: str
    ItemAmt: str
    ItemCount: str
    CarrierType: Optional[Literal["0", "1", "2"]]
    CarrierNum: Optional[str]
    LoveCode: Optional[str]
    PrintFlag: Literal["Y", "N"] = "Y"
    TaxType: Literal["1", "2", "3", "9"] = "1"
    TaxRate: int = 5  # 5%
    CustomsClearance: Optional[Literal["1", "2"]]
    Amt: int
    AmtSales: Optional[int]
    AmtZero: Optional[int]
    AmtFree: Optional[int]
    TaxAmt: int
    TotalAmt: int


class QueryModel(BaseModel):
    SearchType: Optional[Literal["0", "1"]]
    MerchantOrderNo: str
    TotalAmt: str
    InvoiceNumber: str
    RandomNum: str
    DisplayFlag: Optional[Literal["1"]]


class VoidModel(BaseModel):
    InvoiceNumber: str
    InvalidReason: str


class IssueResult(BaseModel):
    CheckCode: str
    MerchantID: str
    MerchantOrderNo: str
    InvoiceNumber: str
    TotalAmt: str
    InvoiceTransNo: str
    RandomNum: str
    CreateTime: str
    BarCode: Optional[str]
    QRcodeL: Optional[str]
    QRcodeR: Optional[str]


class IssueResp(BaseModel):
    Status: str
    Message: str
    Result: Optional[IssueResult]

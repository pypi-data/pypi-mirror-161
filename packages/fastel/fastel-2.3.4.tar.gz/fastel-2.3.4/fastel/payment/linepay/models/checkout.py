from typing import Any, List, Literal, Optional

from pydantic import BaseModel


class CheckoutProduct(BaseModel):
    id: str
    name: str
    imageUrl: Optional[str]
    quantity: int
    price: int


class CheckoutPackage(BaseModel):
    id: str
    amount: int
    products: List[CheckoutProduct]


class CheckoutRedirectUrl(BaseModel):
    confirmUrl: str
    cancelUrl: str


class LinePayCheckoutModel(BaseModel):
    amount: int
    currency: Literal["USD", "JPY", "TWD", "THB"] = "TWD"
    orderId: str
    packages: List[CheckoutPackage]
    redirectUrls: CheckoutRedirectUrl


class LinePayCallbackModel(BaseModel):
    orderId: str
    transactionId: str


class LinePayConfirmModel(BaseModel):
    amount: int
    currency: Literal["USD", "JPY", "TWD", "THB"] = "TWD"
    transactionId: str


class LinePayTransactionDetail(BaseModel):
    transaction_id: str
    order_id: str


class LinePayResponse(BaseModel):
    returnCode: str
    returnMessage: str
    info: Any


class LinePayRequestPaymentUrl(BaseModel):
    app: str
    web: str


class LinePayRequestInfo(BaseModel):
    transactionId: str
    paymentAccessToken: str
    paymentUrl: LinePayRequestPaymentUrl


class LinePayRequestResp(LinePayResponse):
    info: Optional[LinePayRequestInfo]


class LinePayConfirmInfo(BaseModel):
    orderId: str
    transactionId: str
    authorizationExpireDate: Optional[str]
    regKey: Optional[str]
    payInfo: Optional[List[Any]]
    packages: Optional[List[Any]]
    merchantReference: Optional[Any]
    shipping: Optional[Any]


class LinePayConfirmResp(LinePayResponse):
    info: Optional[LinePayConfirmInfo]

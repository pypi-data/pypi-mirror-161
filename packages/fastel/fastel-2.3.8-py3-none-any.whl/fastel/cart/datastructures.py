from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Type, Union

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, validator

from fastel.exceptions import APIException


class BaseCartConfig(BaseModel):
    @classmethod
    def model_with_optional_fields(cls: Type[BaseModel]) -> Type[BaseModel]:
        """Generate a `BaseModel` class with all the same fields as `model` but as optional"""

        class OptionalModel(cls):  # type: ignore
            ...

        for field in OptionalModel.__fields__.values():
            field.required = False

        # for generated schema for example (can be removed)
        OptionalModel.__name__ = f"Optional{cls.__name__}"

        return OptionalModel

    @classmethod
    def validate_optional(cls, value: Any) -> BaseModel:
        return cls.model_with_optional_fields().validate(value)


class PaymentSubTypes(str, Enum):
    atm = "atm"
    credit = "credit"
    cod = "cod"
    offline = "offline"
    linepay = "linepay"
    barcode = "barcode"
    webatm = "webatm"
    cvs = "cvs"
    unknown = "unknown"
    default = "default"  # ecpay payment all open


class LogisticTypes(str, Enum):
    HOME = "HOME"
    CVS = "CVS"
    SELF_PICK = "SELF_PICK"
    CUSTOM = "CUSTOM"


class HomeSubtypes(str, Enum):
    ECAN = "ECAN"
    TCAT = "TCAT"
    SF = "SF"


class InvoiceTypes(str, Enum):
    B2B = "B2B"  # 三聯
    B2C = "B2C"  # 二聯
    B2C_DONATE = "B2C_DONATE"  # 捐贈
    B2C_PHONE_CARRIER = "B2C_PHONE_CARRIER"  # 手機載具
    B2C_NPC = "B2C_NPC"  # 自然人憑證
    B2C_PROVIDER = "B2C_PROVIDER"  # 會員載具


class CVSLogisticSubTypes(str, Enum):
    FAMI = "FAMI"
    UNIMART = "UNIMART"
    HILIFE = "HILIFE"
    FAMIC2C = "FAMIC2C"
    UNIMARTC2C = "UNIMARTC2C"
    HILIFEC2C = "HILIFEC2C"
    OKMARTC2C = "OKMARTC2C"


class CartConfig(BaseCartConfig):
    buyer_name: str = ""
    buyer_phone: str = ""
    buyer_email: EmailStr
    buyer_zip: str = ""
    buyer_city: str = ""
    buyer_district: str = ""
    buyer_address: str = ""
    buyer_tel: str = ""
    buyer_tel_ext: str = ""
    receiver_name: str = ""
    receiver_phone: str = ""
    receiver_email: str = ""
    receiver_zip: str = ""
    receiver_city: str = ""
    receiver_district: str = ""
    receiver_address: str = ""
    receiver_tel: str = ""
    receiver_tel_ext: str = ""
    payment_subtype: PaymentSubTypes = PaymentSubTypes.credit
    logistics_type: LogisticTypes = LogisticTypes.HOME
    logistics_subtype: str = HomeSubtypes.TCAT
    logistics_cvs_store_id: Optional[str]

    invoice_type: InvoiceTypes = InvoiceTypes.B2C_PROVIDER
    b2b_company_name: str = ""
    b2b_company_no: str = ""
    b2c_phone_carrier_code: str = ""
    b2c_donate_code: str = ""
    b2c_npc_code: str = ""
    b2c_provider_code: str = ""

    order_note: str = ""
    points: int = 0
    gift_points: int = 0
    use_full_points: bool = False
    extra_data: Optional[Any]

    @validator("logistics_subtype")
    def validate_logistic_subtype(cls, value: str, values: Dict[str, Any]) -> str:
        if value is None:
            return ""
        try:
            if values["logistics_type"] in [
                LogisticTypes.SELF_PICK,
                LogisticTypes.CUSTOM,
            ]:
                return ""
            elif values["logistics_type"] == LogisticTypes.HOME:
                return HomeSubtypes[value]
            return CVSLogisticSubTypes[value]
        except KeyError:
            raise ValueError("subtype_not_valid")


OptionalCartConfig = CartConfig.model_with_optional_fields()


class SingleConfig(BaseModel):
    name: str
    choice: str


class BoolConfig(BaseModel):
    name: str


class ItemConfig(BaseModel):
    qty: int
    variants: List[Union[SingleConfig, BoolConfig]] = []
    extra_data: Optional[Any]

    @validator("qty")
    def positive_qty(cls, qty: int) -> int:
        if qty < 1:
            raise APIException(
                status_code=400, error="invalid_qty_error", detail="quantity must > 0"
            )
        return qty

    @validator("variants")
    def validate_variants(
        cls, value: List[Union[SingleConfig, BoolConfig]]
    ) -> List[Union[SingleConfig, BoolConfig]]:
        names = []
        for variant in value:
            if variant.name in names:
                raise APIException(status_code=400, error="invalid_variant", detail="")
            names.append(variant.name)

        return value


class VariantTypes(str, Enum):
    bool = "bool"
    single = "single"


class SingleChoice(BaseModel):
    name: str
    label: str
    price: int


class SingleVariant(BaseModel):
    type: Literal["single"]
    name: str
    label: str
    choices: List[SingleChoice]


class BooleanVariant(BaseModel):
    type: Literal["bool"]
    name: str
    label: str
    price: int


class ValidatedObjectId(ObjectId):  # type: ignore
    @classmethod
    def __get_validators__(cls) -> Any:
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        return ObjectId(value)


class Product(BaseModel):
    id: ValidatedObjectId = Field(alias="_id")
    name: str
    price: int
    stock_type: Optional[Literal["always", "period", "total"]] = "always"
    stock_amount: Optional[int] = 0
    stock_sold_amount: Optional[int] = 0
    stock_start_date: Optional[str]
    stock_start_time: Optional[str]
    stock_end_date: Optional[str]
    stock_end_time: Optional[str]
    variants: List[Union[SingleVariant, BooleanVariant]] = []
    on_shelf: Optional[bool]
    public: Optional[bool]
    labels: Optional[List[str]]
    images: Optional[Union[List[str], List[Dict[str, Any]]]]
    extra_data: Optional[Any]

    class Config:
        allow_population_by_field_name = True


class Coupon(BaseModel):
    id: ValidatedObjectId = Field(alias="_id")
    name: str
    code: str
    discount: int
    threshold: int
    start_time: int
    end_time: int
    usage: int = 0


class Discount(BaseModel):
    id: ValidatedObjectId = Field(alias="_id")
    name: str
    discount: int
    threshold: int
    start_time: int
    end_time: int

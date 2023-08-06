# ecpay
from typing import Any, Dict, List

from fastel.cart.datastructures import InvoiceTypes, PaymentSubTypes
from fastel.payment.ecpay.models.invoice import IssueB2BModel, IssueB2CModel

ECPAY_CALLBACK_SUBTYPE = {
    "Credit": PaymentSubTypes.credit,
    "ATM": PaymentSubTypes.atm,
    "WebATM": PaymentSubTypes.webatm,
    "CVS": PaymentSubTypes.cvs,
    "BARCODE": PaymentSubTypes.barcode,
}

CARRIER_TYPE_TABLE = {
    InvoiceTypes.B2C: "",
    InvoiceTypes.B2C_DONATE: "",
    InvoiceTypes.B2C_PROVIDER: "1",
    InvoiceTypes.B2C_NPC: "2",
    InvoiceTypes.B2C_PHONE_CARRIER: "3",
}


def _replace_limit_name(name: str, limit: int) -> str:
    if len(name) > limit:
        return name[: limit - 3] + "..."
    return name


def generate_B2B_invoice_data(order: Dict[str, Any]) -> Dict[str, Any]:
    items = order.get("items", [])
    extra_items = order.get("extra_items", [])
    discount_items = order.get("discount_items", [])
    invoice_data = {
        "RelateNumber": order.get("order_number", ""),
        "CustomerIdentifier": order.get("b2b_company_no", ""),
        "CustomerAddress": order.get("buyer_city", "")
        + order.get("buyer_district", "")
        + order.get("buyer_address"),
        "CustomerEmail": order.get("buyer_email", ""),
        "TaxType": "1",
        "SalesAmount": order.get("sales", 0),
        "TaxAmount": order.get("tax", 0),
        "TotalAmount": order.get("total", 0),
        "Items": generate_B2B_invoice_item(items, extra_items, discount_items),
        "InvType": "07",
    }
    return IssueB2BModel.validate(invoice_data).dict(exclude_none=True)


def generate_B2B_invoice_item(
    items: List[Dict[str, Any]],
    extra_items: List[Dict[str, Any]],
    discount_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    result = []
    seq = 1
    for item in items:
        item_result = {
            "ItemSeq": seq,
            "ItemName": _replace_limit_name(name=item.get("name", ""), limit=256),
            "ItemCount": item["config"].get("qty", 1),
            "ItemWord": item["config"]["extra_data"]
            and item["config"]["extra_data"].get("word", "份")
            or "份",
            "ItemPrice": item.get("unit_sales", 0),
            "ItemAmount": item.get("sales_amount", 0),
        }
        result.append(item_result)
        seq += 1
    # 計算運費
    for extra_item in extra_items:
        item_result = {
            "ItemSeq": seq,
            "ItemName": _replace_limit_name(name=extra_item.get("name", ""), limit=256),
            "ItemCount": 1,
            "ItemWord": "份",
            "ItemPrice": round(extra_item.get("amount", 0) / 1.05, 7),
            "ItemAmount": round(extra_item.get("amount", 0) / 1.05, 7),
        }
        result.append(item_result)
        seq += 1
    # 計算折扣金額
    for discount_item in discount_items:
        item_result = {
            "ItemSeq": seq,
            "ItemName": _replace_limit_name(
                name=discount_item.get("name", ""), limit=256
            ),
            "ItemCount": 1,
            "ItemWord": "份",
            "ItemPrice": -discount_item.get("sale_amount", 0),
            "ItemAmount": -discount_item.get("sale_amount", 0),
        }
        result.append(item_result)
        seq += 1
    return result


def generate_B2C_invoice_data(order: Dict[str, Any]) -> Dict[str, Any]:
    items = order.get("items", [])
    extra_items = order.get("extra_items", [])
    discount_items = order.get("discount_items", [])
    carrier_type = CARRIER_TYPE_TABLE[order["invoice_type"]]
    if order["invoice_type"] == InvoiceTypes.B2C:
        print = "1"
        donation = "0"
        carrier_num = ""
        love_code = None
    elif order["invoice_type"] == InvoiceTypes.B2C_PROVIDER:
        print = "0"
        donation = "0"
        carrier_num = ""
        love_code = None
    elif order["invoice_type"] == InvoiceTypes.B2C_NPC:
        print = "0"
        donation = "0"
        carrier_num = order.get("b2c_npc_code", "")
        love_code = None
    elif order["invoice_type"] == InvoiceTypes.B2C_PHONE_CARRIER:
        print = "0"
        donation = "0"
        carrier_num = order.get("b2c_phone_carrier_code", "")
        love_code = None
    elif order["invoice_type"] == InvoiceTypes.B2C_DONATE:
        print = "0"
        donation = "1"
        love_code = order.get("b2c_donate_code", "")
        carrier_num = ""
    else:
        print = "0"
        donation = "0"
        carrier_num = ""
        love_code = None
    invoice_data = {
        "RelateNumber": order.get("order_number", ""),
        "CustomerName": order.get("buyer_name", ""),
        "CustomerAddr": order.get("buyer_city", "")
        + order.get("buyer_district", "")
        + order.get("buyer_address"),
        "CustomerEmail": order.get("buyer_email", ""),
        "Print": print,
        "Donation": donation,
        "LoveCode": love_code,
        "CarrierType": carrier_type,
        "CarrierNum": carrier_num,
        "TaxType": "1",
        "SalesAmount": order.get("total", 0),
        "Items": generate_B2C_invoice_item(items, extra_items, discount_items),
        "InvType": "07",
    }
    return IssueB2CModel.validate(invoice_data).dict(exclude_none=True)


def generate_B2C_invoice_item(
    items: List[Dict[str, Any]],
    extra_items: List[Dict[str, Any]],
    discount_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    result = []
    for item in items:
        item_result = {
            "ItemName": _replace_limit_name(name=item.get("name", ""), limit=100),
            "ItemCount": item["config"].get("qty", 1),
            "ItemWord": item["config"]["extra_data"]
            and item["config"]["extra_data"].get("word", "份")
            or "份",
            "ItemPrice": item.get("price", 0),
            "ItemAmount": item.get("amount", 0),
        }
        result.append(item_result)
    # 計算運費
    for extra_item in extra_items:
        item_result = {
            "ItemName": _replace_limit_name(name=extra_item.get("name", ""), limit=100),
            "ItemCount": 1,
            "ItemWord": "份",
            "ItemPrice": extra_item.get("amount", 0),
            "ItemAmount": extra_item.get("amount", 0),
        }
        result.append(item_result)
    # 計算折扣金額
    for discount_item in discount_items:
        item_result = {
            "ItemName": _replace_limit_name(
                name=discount_item.get("name", ""), limit=100
            ),
            "ItemCount": 1,
            "ItemWord": "份",
            "ItemPrice": -discount_item.get("amount", 0),
            "ItemAmount": -discount_item.get("amount", 0),
        }
        result.append(item_result)
    return result

from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel


class InvoiceStatus(str, Enum):
    success = "success"
    failure = "failure"
    pending = "pending"


class InvoiceIssueResp(BaseModel):
    status: InvoiceStatus
    invoice_number: str
    invoice_message: str
    invoice_detail: Dict[str, Any]
    invoice_random_no: str

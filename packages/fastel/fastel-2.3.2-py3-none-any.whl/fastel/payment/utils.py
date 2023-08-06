from datetime import datetime, timezone
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    WAITING = "waiting"
    SUCCESS = "success"
    FAILURE = "failure"
    CODE_GENERATED = "code_generated"


def auto_order_number() -> str:
    order_number = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")[:-2]
    return order_number

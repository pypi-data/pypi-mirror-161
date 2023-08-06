# utils
import time

import pytz

TW = pytz.timezone("Asia/Taipei")


def default_timestamp() -> int:
    return round(time.time() * 1000)


def timestamp_postfix(name: str) -> str:
    return name + "_" + str(int(time.time()))

import io

import boto3

from fastel.config import SdkConfig
from fastel.logistics.common.helpers import get_shipping_note_method
from fastel.logistics.common.models import LogisticsDataModel


def upload_shipping_note(logistics_data: LogisticsDataModel) -> None:
    try:
        method = get_shipping_note_method("ecpay")
        shipping_note, content_type = method(logistics_data.dict(exclude_none=True))
        s3 = boto3.client("s3", "ap-northeast-1")
        buf = io.BytesIO()
        buf.write(shipping_note)
        buf.seek(0)
        s3.upload_fileobj(
            buf,
            SdkConfig.s3_bucket,
            f"shipping_note/{logistics_data.logistics_id}",
            # shipping note must be private file
            ExtraArgs={"ContentType": content_type},
        )
        print(
            "[UPLOAD SHIPPING] ------------------------- SUCCESS ------------------------"
        )
    except Exception as error:
        print(
            "[UPLOAD SHIPPING] ------------------------- FAIL ------------------------"
        )
        print(error)
        raise

import json
import os
from base64 import b64decode
from typing import Any, Dict


class SdkConfigCls:
    api_host: str = ""
    web_host: str = ""
    sdk_client: str = ""
    stage: str = ""
    client_secret: str = ""
    conversion_id: str = ""
    conversion_token: str = ""

    s3_bucket: str = ""

    sf_merchant_id: str = ""
    sf_aes_key: str = ""
    sf_app_key: str = ""
    sf_secret: str = ""
    sf_card_no: str = ""

    payment_stepfn_arn: str = ""
    logistics_stepfn_arn: str = ""

    neweb_merchant_id: str = ""
    neweb_hash_key: str = ""
    neweb_hash_iv: str = ""

    neweb_invoice_merchant_id: str = ""
    neweb_invoice_hash_key: str = ""
    neweb_invoice_hash_iv: str = ""

    ecpay_merchant_id: str = ""
    ecpay_hash_key: str = ""
    ecpay_hash_iv: str = ""

    ecpay_invoice_merchant_id: str = ""
    ecpay_invoice_hash_key: str = ""
    ecpay_invoice_hash_iv: str = ""

    ecpay_logistics_merchant_id: str = ""
    ecpay_logistics_hash_key: str = ""
    ecpay_logistics_hash_iv: str = ""

    linepay_channel_id: str = ""
    linepay_channel_secret: str = ""

    public_key: Dict[str, Any]
    auth_host: str
    ntfn_host: str

    extra_config: Dict[str, Any] = {}

    @property
    def provider(self) -> str:
        parts = self.sdk_client.split(".")
        return parts[0]

    @property
    def client_id(self) -> str:
        parts = self.sdk_client.split(".")
        return parts[-1]

    @property
    def is_service(self) -> bool:
        return True if self.provider == "service" else False

    @property
    def ecpay_logistics_host(self) -> str:
        if self.stage in ["stg", "dev"]:
            return "https://logistics-stage.ecpay.com.tw"
        elif self.stage in ["prod", "production"]:
            return "https://logistics.ecpay.com.tw"
        else:
            return ""

    def put_extras(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            self.extra_config[key] = value

    def get_extra(self, key: str, default_value: Any = None) -> Any:
        return self.extra_config.get(key, default_value)


SdkConfig = SdkConfigCls()


def sdk_auto_config(sdk_client: str = "") -> None:
    global SdkConfig
    print("SdkConfig", SdkConfig)

    def get_env_or_raise(key: str, raise_exception: bool = True) -> str:
        value: str = os.environ.get(key, "")
        if value == "" and raise_exception:
            raise AttributeError(f"[sdk_auto_config] {key} not found")
        return value

    # if not sdk_client initial app by revtel
    if not sdk_client:
        client_id = get_env_or_raise("CLIENT_ID")
        sdk_client = f"app.{client_id}"

    # common env vars
    SdkConfig.stage = get_env_or_raise("STAGE")

    b64_public = get_env_or_raise("PUBLIC_KEY")
    SdkConfig.public_key = json.loads(b64decode(b64_public.encode("UTF-8")).decode())
    SdkConfig.auth_host = get_env_or_raise("AUTH_HOST", False)
    SdkConfig.ntfn_host = get_env_or_raise("NTFN_HOST", False)

    SdkConfig.sdk_client = sdk_client

    if not SdkConfig.is_service:
        SdkConfig.client_secret = get_env_or_raise("CLIENT_SECRET")
        # for facebook conversion vars
        SdkConfig.conversion_id = get_env_or_raise(
            "CONVERSION_ID", raise_exception=False
        )
        SdkConfig.conversion_token = get_env_or_raise(
            "CONVERSION_TOKEN", raise_exception=False
        )
        SdkConfig.payment_stepfn_arn = get_env_or_raise("PAYMENT_STEPFN_ARN", False)
        SdkConfig.logistics_stepfn_arn = get_env_or_raise("LOGISTICS_STEPFN_ARN", False)
        SdkConfig.neweb_merchant_id = get_env_or_raise("NEWEB_MERCHANT_ID", False)
        SdkConfig.neweb_hash_key = get_env_or_raise("NEWEB_HASH_KEY", False)
        SdkConfig.neweb_hash_iv = get_env_or_raise("NEWEB_HASH_IV", False)

        SdkConfig.neweb_invoice_merchant_id = get_env_or_raise(
            "NEWEB_INVOICE_MERCHANT_ID", False
        )
        SdkConfig.neweb_invoice_hash_key = get_env_or_raise(
            "NEWEB_INVOICE_HASH_KEY", False
        )
        SdkConfig.neweb_invoice_hash_iv = get_env_or_raise(
            "NEWEB_INVOICE_HASH_IV", False
        )

        SdkConfig.ecpay_merchant_id = get_env_or_raise("ECPAY_MERCHANT_ID", False)
        SdkConfig.ecpay_hash_key = get_env_or_raise("ECPAY_HASH_KEY", False)
        SdkConfig.ecpay_hash_iv = get_env_or_raise("ECPAY_HASH_IV", False)

        SdkConfig.ecpay_invoice_merchant_id = get_env_or_raise(
            "ECPAY_INVOICE_MERCHANT_ID", False
        )
        SdkConfig.ecpay_invoice_hash_key = get_env_or_raise(
            "ECPAY_INVOICE_HASH_KEY", False
        )
        SdkConfig.ecpay_invoice_hash_iv = get_env_or_raise(
            "ECPAY_INVOICE_HASH_IV", False
        )
        SdkConfig.linepay_channel_id = get_env_or_raise("LINEPAY_CHANNEL_ID", False)
        SdkConfig.linepay_channel_secret = get_env_or_raise(
            "LINEPAY_CHANNEL_SECRET", False
        )

        SdkConfig.ecpay_logistics_merchant_id = get_env_or_raise(
            "ECPAY_LOGISTICS_MERCHANT_ID", False
        )
        SdkConfig.ecpay_logistics_hash_key = get_env_or_raise(
            "ECPAY_LOGISTICS_HASH_KEY", False
        )
        SdkConfig.ecpay_logistics_hash_iv = get_env_or_raise(
            "ECPAY_LOGISTICS_HASH_IV", False
        )

        SdkConfig.api_host = get_env_or_raise("API_HOST", False)
        SdkConfig.web_host = get_env_or_raise("WEB_HOST", False)
        SdkConfig.s3_bucket = get_env_or_raise("S3_BUCKET", False)
        SdkConfig.sf_merchant_id = get_env_or_raise("SF_MERCHANT_ID", False)
        SdkConfig.sf_aes_key = get_env_or_raise("SF_AES_KEY", False)
        SdkConfig.sf_app_key = get_env_or_raise("SF_APP_KEY", False)
        SdkConfig.sf_secret = get_env_or_raise("SF_SECRET", False)
        SdkConfig.sf_card_no = get_env_or_raise("SF_CARD_NO", False)

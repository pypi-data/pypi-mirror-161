import os
from typing import Any, Dict

# https://keys.revtel-api.com/certs.json
prod_cert = {
    "keys": [
        {
            "e": "AQAB",
            "kid": "bc36e546-f24a-4635-a77b-eecb20602504",
            "kty": "RSA",
            "n": "8oPMlKMnG9Uvyr8SMSLf5N7pl2ciEL-OWkAYngAzV1Y492cH8PWWFCibpiXU6iNlBbP_py2O6p8xfMHX1vGCF9uFU__iqc5RBbaCYL1kxczQbCt69tPLdyv3_6FNfMioc62Cym77rEVIa4uRLJl0TB_BJ89beCoL7BO6U1szGz3oVn-4igsc8GQRJOaZkZXY0JIBqB7dTHBgiq1R444ex_Tl1M6E9w45PxzowLOn1GWv6X5wyOSX1z-g60ErmDdxuu3N3lm2fJr9W-mjFgMvo4V9tBQmABaWO573I82IJymxt3C6B1g9Co9P1Thk5zMxtm33Om2FrizinUZbnQAtqQ",
        },
        {
            "e": "AQAB",
            "kid": "d4601977-6244-4a01-87dd-af0c1855886a",
            "kty": "RSA",
            "n": "yrIO_j-qbZfDlbLaTF-TQC38LVv8FVaXV4RPwNwSL_3QQA04HO1lnA8eXf2jV3RbI3WVey9jgDxjIidGAQQ0EJawXX7lPKWj56gDWBjPID7z-32DXicPww7vAgP8KD_GD00bwDnrnPCEveZQ9fAX-9zJpDNLRZlZ-GdgwOP55dIUFaOGeS1GP3jCBcy9auRzthBV4CO2Y_WzC69yL-4WgBPY_cIEc49vZ_Xyyo2mP36-fHzJc9eQ-moRczJ_hlCUe6DPfC99ojMFxXyd9SkD6BvTdnI5Bw-DPd4MCQj6KeSTuWTVfi2zsL2ooX0e8oLqmdhKqEB7T9LAr2efJkBGQQ",
        },
    ]
}

# https://keys.revtel-api.com/certs-stg.json
stg_cert = {
    "keys": [
        {
            "e": "AQAB",
            "kid": "df9885fa-942b-40c0-988c-9c3af76694bc",
            "kty": "RSA",
            "n": "x_-UkGLNQVRBXXW894iokDf7irGQ8rNPzsp-9N4ylVrkES93OL95E_rOdoK0Z8kCuwPOvKfc1QmgBFoJjMMaxI3zLDdDTl9QRIS1e1akecuAdzMj53X_t98Z2pgcT1paoDSkHh7qgYRKmt1xpU7fbKrogjdzqTv3vsnB3tQU2P1-9UJtH3-1BoAVhyiusFqXLH0o6Rp7drMbVYbvyj19nRwcBZz9gtO_bWyYGz0KUtFkm_vc31JmCARif7Tb4vc6FsmjGCgaQ9OSbJLgmYS7ZeVLFomyLKZuDeyAbS0rfzjC6Cf5heu6F2F44MdRoq-QK88nZ19fOpcJk1CkYPtySQ",
        },
        {
            "e": "AQAB",
            "kid": "1a7f2fbe-5112-4450-b7f1-27187d6030fb",
            "kty": "RSA",
            "n": "nPPHuzGJ8M9eZVr2f_CUrzFzyPQ0Ks9R31abO2B6qSOKQb_7aLQC7kOB02wWckyqpKhMRHTVbpKBJXYI1sga_iAaFfDyJ8-RVH3-hbpF1-_Bv7AteGJSZe2Etyi4kFXSZs2pDNOgUS6zvrkdQTlIqSst6MGJNKiaF1OpsmYlwAzJF37YAbrkuNOC1nbQorKkqQzSDa9667ZiEGoU65TGWP0FWwuzSBJGb8AOVNIEdIUaEdTrimoENzJOJR-RHeRGPLpU_Fe7TRj_RLyixDB6Hp_ZyYHW3Su7N3YBu2vZnp42d29E1UMFCU6k_5uoWR6rvosxCL1FkfaoXvpQ78oDmQ",
        },
    ]
}


dsa_cert = {
    "keys": [
        {
            "e": "AQAB",
            "kid": "428ab35b-9743-4034-bc95-87035411056b",
            "kty": "RSA",
            "n": "oAadb4E0B6vniuTjfFpybq314GkHMPVCxgQ-6a_a0Xo_HZrTsb-1ANC4GriFcJdswMJWRDO22RLE-1WTRyoW68HZ9YKzu6ZaRViAX4ihJXPeTF0uiqf9A9wAuSt5ZzLB4dVh9QJavwM1IaaxIzMhfeM1ykAd6bj1RazO9FatfhqJJbqsbCi_Ze4nUq4hrFsVkMXJBNew7yEBc6_NKUuLDYTOhdT-w9Rj6BM152Um-lEg27ENZCxJ5i_AhStw4in-Pk7V4yBPuscAqNiUSUUYc28ZmsX8T9KUBOPmiOAmbbYHmP7KZx3Gf5xqgxjL8NfMseOK5S9G-Cjsgy5eJYOM4Q",
        }
    ]
}


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

    extra_config: Dict[str, Any] = {}

    @property
    def provider(self) -> str:
        parts = self.sdk_client.split(".")
        return parts[0]

    @property
    def client_id(self) -> str:
        parts = self.sdk_client.split(".")
        return parts[1]

    @property
    def package(self) -> str:
        parts = self.sdk_client.split(".")
        return parts[-1]

    @property
    def is_service(self) -> bool:
        return True if self.provider == "service" else False

    @property
    def auth_host(self) -> str:
        if self.stage in ["stg", "dev"] and self.package == "revtel":
            return "https://auth-stg.revtel-api.com/v4"
        elif self.stage in ["prod", "production"] and self.package == "revtel":
            return "https://auth.revtel-api.com/v4"
        elif self.stage == "prod" and self.package == "DSA":
            return "https://auth.dsa-automation.com.tw/v4"
        else:
            return ""

    @property
    def ntfn_host(self) -> str:
        if self.stage == "stg" and self.package == "revtel":
            return "https://notification-stg.revtel-api.com/v4"
        elif self.stage in ["prod", "production"] and self.package == "revtel":
            return "https://notification.revtel-api.com/v4"
        elif self.stage == "dev" and self.package == "revtel":
            return "https://notification-dev.revtel-api.com/v4"
        else:
            return ""

    @property
    def payment_host(self) -> str:
        if self.stage in ["stg", "dev"] and self.package == "revtel":
            return "https://payment-stg.revtel-api.com/v3"
        elif self.stage in ["prod", "production"] and self.package == "revtel":
            return "https://payment.revtel-api.com/v3"
        else:
            return ""

    @property
    def ecpay_logistics_host(self) -> str:
        if self.stage in ["stg", "dev"]:
            return "https://logistics-stage.ecpay.com.tw"
        elif self.stage in ["prod", "production"]:
            return "https://logistics.ecpay.com.tw"
        else:
            return ""

    @property
    def public_key(self) -> Dict[str, Any]:
        if self.stage == "stg" and self.package == "revtel":
            return stg_cert
        elif self.stage in ["prod", "production"] and self.package == "revtel":
            return prod_cert
        elif self.stage in ["prod", "production"] and self.package == "DSA":
            return dsa_cert
        else:
            return {}

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
        sdk_client = f"app.{client_id}.revtel"

    # common env vars
    SdkConfig.stage = get_env_or_raise("STAGE")

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

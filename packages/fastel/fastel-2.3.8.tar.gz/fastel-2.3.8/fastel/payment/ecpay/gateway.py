import time
from datetime import datetime
from typing import Any, Dict

import requests

from fastel.payment.cryptors import EcInvoiceCryptor, SHACryptor
from fastel.payment.ecpay.models.checkout import EcCheckoutModel


class Ecpay:
    def __init__(
        self, merchant_id: str, hash_key: str, hash_iv: str, stage: str = "stg"
    ) -> None:
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.stage = stage
        self.cryptor = SHACryptor(hash_key, hash_iv)

    @property
    def payment_host(self) -> str:
        if self.stage in ["prod", "PROD"]:
            return "https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5"
        return "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"

    def checkout_request(self, checkout: EcCheckoutModel) -> str:
        payload = checkout.dict()
        now = datetime.now()
        gateway_payload: Dict[str, Any] = {
            **payload,
            "MerchantID": self.merchant_id,
            "PaymentType": "aio",
            "EncryptType": 1,
            "MerchantTradeDate": now.strftime("%Y/%m/%d %H:%M:%S"),
        }
        trade_info = self.cryptor.encrypt(gateway_payload)
        checkout_payload = {**gateway_payload, "CheckMacValue": trade_info}
        row_payload = "\n".join(
            map(
                lambda k: f'<input type="hidden" name="{k[0]}" value="{k[1]}"><br>',
                checkout_payload.items(),
            )
        )
        formdata_payload = f"""
                <html>
                  <body>
                      <form name="ecpay" method="post" action="{self.payment_host}">
                          {row_payload}
                          <input type="hidden" value="Submit"><br>
                      </form>
                      </body>
                      <script type="text/javascript">ecpay.submit();
                  </script>
                </html>
                """

        return formdata_payload


class EcpayInvoice:
    def __init__(
        self, merchant_id: str, hash_key: str, hash_iv: str, stage: str = "stg"
    ) -> None:
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.stage = stage
        self.cryptor = EcInvoiceCryptor(hash_key, hash_iv)

    @property
    def invoice_url(self) -> str:
        if self.stage in ["prod", "PROD"]:
            return "https://einvoice.ecpay.com.tw/"
        else:
            return "https://einvoice-stage.ecpay.com.tw/"

    def issue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        encrypted_payload = {
            "MerchantID": self.merchant_id,
            "RqHeader": {
                "Timestamp": str(int(time.time())),
                "Revision": "3.0.0",
            },
            "Data": self.cryptor.encrypt(data),
        }

        try:
            invoice_path = (
                "B2BInvoice/Issue"
                if data.get("CustomerIdentifier", "")
                else "B2CInvoice/Issue"
            )
            resp = requests.post(
                f"{self.invoice_url}/{invoice_path}", json=encrypted_payload
            )
            resp.raise_for_status()
            resp_json = resp.json()
            assert isinstance(resp_json, dict)
            if isinstance(resp_json["Data"], str) and resp_json["TransCode"] == 1:
                result = resp_json
                result["Data"] = self.cryptor.decrypt(resp_json["Data"])
            else:
                result = resp_json
        except requests.HTTPError as exc:
            result = {"error": exc.response.json()}

        return result

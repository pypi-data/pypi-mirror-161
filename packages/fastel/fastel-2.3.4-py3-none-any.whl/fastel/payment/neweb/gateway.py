import json
import time

import requests

from fastel.payment.cryptors import AESCryptor
from fastel.payment.neweb.models.callback import (
    CallbackMsg,
    EncryptedCallback,
    GetNumMsg,
)
from fastel.payment.neweb.models.checkout import CheckoutModel
from fastel.payment.neweb.models.invoice import IssueModel, IssueResp


class Newebpay:
    def __init__(
        self, merchant_id: str, hash_key: str, hash_iv: str, stage: str = "stg"
    ) -> None:
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.stage = stage
        self.cryptor = AESCryptor(hash_key, hash_iv)

    @property
    def payment_host(self) -> str:
        if self.stage in ["prod", "PROD"]:
            return "https://core.newebpay.com/MPG/mpg_gateway"
        return "https://ccore.newebpay.com/MPG/mpg_gateway"

    def checkout_request(self, checkout: CheckoutModel) -> str:
        checkout.MerchantID = self.merchant_id

        payload = checkout.dict()
        trade_info = self.cryptor.encrypt(payload)

        gateway_payload = {
            "MerchantID": self.merchant_id,
            "TradeInfo": trade_info,
            "TradeSha": self.cryptor.build_trade_sha(trade_info),
            "Version": "1.5",
        }

        row_payload = "\n".join(
            map(
                lambda k: f'<input type="hidden" name="{k[0]}" value="{k[1]}"><br>',
                gateway_payload.items(),
            )
        )
        formdata_payload = f"""
                <html>
                  <body>
                      <form name="neweb" method="post" action="{self.payment_host}">
                          {row_payload}
                          <input type="hidden" value="Submit"><br>
                      </form>
                      </body>
                      <script type="text/javascript">neweb.submit();
                  </script>
                </html>
                """

        return formdata_payload

    def decrypt_callback(self, encrypted_callback: EncryptedCallback) -> CallbackMsg:
        decrypted = self.cryptor.decrypt(encrypted_callback.TradeInfo)
        return CallbackMsg.validate(json.loads(decrypted))

    def decrypt_getnum(self, encrypted_callback: EncryptedCallback) -> GetNumMsg:
        decrypted = self.cryptor.decrypt(encrypted_callback.TradeInfo)
        return GetNumMsg.validate(json.loads(decrypted))


class NewebInvoice:
    def __init__(
        self, merchant_id: str, hash_key: str, hash_iv: str, stage: str = "stg"
    ) -> None:
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.stage = stage
        self.cryptor = AESCryptor(hash_key, hash_iv)

    @property
    def invoice_url(self) -> str:
        if self.stage in ["prod", "PROD"]:
            return "https://inv.ezpay.com.tw/Api"
        else:
            return "https://cinv.ezpay.com.tw/Api"

    def issue(self, data: IssueModel) -> IssueResp:
        payload = {
            "RespondType": "JSON",
            "Version": "1.4",
            "TimeStamp": str(int(time.time())),
            **data.dict(exclude_none=True),
        }
        encrypted_payload = {
            "MerchantID_": self.merchant_id,
            "PostData_": self.cryptor.encrypt(payload),
        }

        try:
            resp = requests.post(
                f"{self.invoice_url}/invoice_issue", data=encrypted_payload
            )
            resp.raise_for_status()
            resp_json = resp.json()
            if isinstance(resp_json["Result"], str):
                resp_json["Result"] = json.loads(resp_json["Result"])
            else:
                resp_json["Result"] = None

            resp_model = IssueResp.validate(resp_json)
        except requests.HTTPError as exc:
            err_resp = exc.response.json()
            resp_model = IssueResp.validate(err_resp)

        return resp_model

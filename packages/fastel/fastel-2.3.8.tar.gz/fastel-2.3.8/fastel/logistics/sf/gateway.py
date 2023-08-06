import json
import time
from typing import Any, Dict, Tuple

# from fastel.utils import requests
import requests
from requests import Response

from fastel.exceptions import APIException
from fastel.logistics.sf import api_token
from fastel.logistics.sf.cryptor import SFCryptor
from fastel.logistics.sf.models import SFLogisticsModel


class SFLogistics:
    def __init__(
        self,
        merchant_id: str,
        aes_key: str,
        app_key: str,
        secret: str,
        stage: str = "stg",
    ) -> None:
        self.merchant_id = merchant_id
        self.aes_key = aes_key
        self.app_key = app_key
        self.secret = secret
        self.stage = stage
        self.sf_token = api_token(self.logistics_url, self.app_key, self.secret)

    @property
    def cryptor(self) -> SFCryptor:
        return SFCryptor(self.aes_key, self.app_key, self.sf_token)

    @property
    def logistics_url(self) -> str:
        if self.stage in ["stg", "STG"]:
            return "http://api-ifsp.sit.sf.global"
        return "https://api-ifsp.sf.global"

    def generate_headers(self, method: str = "IECS_CREATE_ORDER") -> Dict[str, Any]:
        timestamp = str(int(time.time()))
        headers = {
            "appKey": self.app_key,
            "token": self.sf_token,
            "timestamp": timestamp,
            "nonce": timestamp,
            "msgType": method,
            "Content-Type": "application/json",
        }
        return headers

    def encrypt_data(
        self, data: Dict[str, Any], method: str = "IECS_CREATE_ORDER"
    ) -> Tuple[Dict[str, Any], str]:
        msg = json.dumps(data, ensure_ascii=False)
        headers = self.generate_headers(method)
        print(headers)
        ret_code, encrypt, signature = self.cryptor.encrypt_msg(
            msg=msg, nonce=headers["nonce"], timestamp=headers["timestamp"]
        )
        if ret_code != 0:
            raise APIException(status_code=400, error="SF_Encrypt_Error", detail="")

        headers = {**headers, "signature": signature}
        if encrypt:
            return headers, encrypt
        else:
            return headers, ""

    def create_logistics(self, data: SFLogisticsModel) -> Dict[str, Any]:
        url = self.logistics_url + "/openapi/api/dispatch"

        headers, body = self.encrypt_data(
            data=data.dict(exclude_none=True), method="IUOP_CREATE_ORDER"
        )
        resp: Response = requests.post(url, headers=headers, data=body)
        logistics_resp: Dict[str, Any] = resp.json()
        ret, result = self.cryptor.decrypt_msg(
            post_data=logistics_resp.get("apiResultData", "")
        )
        assert isinstance(result, dict)
        return result

    def query_track(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self.logistics_url + "/openapi/api/dispatch"
        headers, body = self.encrypt_data(data=data, method="IUOP_QUERY_TRACK")
        resp: Response = requests.post(url, headers=headers, json=body)
        logistics_resp: Dict[str, Any] = resp.json()

        ret, result = self.cryptor.decrypt_msg(
            post_data=logistics_resp.get("apiResultData", "")
        )
        assert isinstance(result, dict)
        return result

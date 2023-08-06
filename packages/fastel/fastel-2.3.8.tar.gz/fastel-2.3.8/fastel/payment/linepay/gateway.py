import json
import uuid
from typing import Any, Dict

import requests

from fastel.payment.cryptors import HMACCryptor
from fastel.payment.linepay.models.checkout import (
    LinePayCheckoutModel,
    LinePayConfirmModel,
    LinePayConfirmResp,
    LinePayRequestResp,
    LinePayResponse,
    LinePayTransactionDetail,
)


class LinePay:
    def __init__(
        self,
        channel_id: str,
        channel_secret: str,
        stage: str = "stg",
    ):
        self.channel_id = channel_id
        self.channel_secret = channel_secret
        self.stage = stage
        self.cryptor = HMACCryptor(self.channel_secret)

    @property
    def payment_host(self) -> str:
        if self.stage in ["prod", "PROD"]:
            return "https://api-pay.line.me"
        return "https://sandbox-api-pay.line.me"

    def build_headers(
        self,
        uri: str,
        data_str: str,
    ) -> Dict[str, Any]:
        nonce = str(uuid.uuid4())
        signature = self.cryptor.encrypt(nonce, uri, data_str)
        return {
            "Content-Type": "application/json",
            "X-LINE-ChannelId": self.channel_id,
            "X-LINE-Authorization-Nonce": nonce,
            "X-LINE-Authorization": signature,
        }

    def checkout_request(self, checkout: LinePayCheckoutModel) -> LinePayRequestResp:
        body = checkout.dict()
        path = "/v3/payments/request"
        url = f"{self.payment_host}{path}"
        payload = json.dumps(body)
        headers = self.build_headers(path, payload)
        try:
            resp = requests.post(
                url=url,
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            resp_json = resp.json()
            resp_model = LinePayRequestResp.validate(resp_json)
        except requests.HTTPError as exc:
            resp_json = {"error": exc.response.json()}
            resp_model = LinePayRequestResp.validate(resp_json)

        assert isinstance(resp_model, LinePayRequestResp)
        return resp_model

    def checkout_confirm(self, confirm: LinePayConfirmModel) -> LinePayConfirmResp:
        body = confirm.dict()
        transaction_id = body.pop("transactionId", None)
        path = f"/v3/payments/{transaction_id}/confirm"
        payload = json.dumps(body)
        url = f"{self.payment_host}{path}"
        headers = self.build_headers(path, payload)
        try:
            resp = requests.post(
                url=url,
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            resp_json = resp.json()
            resp_model = LinePayConfirmResp.validate(resp_json)
        except requests.HTTPError as exc:
            resp_json = {"error": exc.response.json()}
            resp_model = LinePayConfirmResp.validate(resp_json)

        assert isinstance(resp_model, LinePayConfirmResp)
        return resp_model

    def get_details(self, data: LinePayTransactionDetail) -> LinePayResponse:
        path = "/v3/payments"
        query = ""
        if data.transaction_id is not None:
            query += "transactionId={}&".format(str(data.transaction_id))
        if data.order_id is not None:
            query += "orderId={}".format(data.order_id)
        if query.endswith("?") or query.endswith("&"):
            query = query[:-1]

        url = (
            query
            and f"{self.payment_host}{path}?{query}"
            or f"{self.payment_host}{path}"
        )

        headers = self.build_headers(path, query)
        try:
            resp = requests.get(
                url=url,
                headers=headers,
            )
            resp.raise_for_status()
            resp_json = resp.json()
            resp_model = LinePayResponse.validate(resp_json)
        except requests.HTTPError as exc:
            resp_json = {"error": exc.response.json()}
            resp_model = LinePayResponse.validate(resp_json)

        assert isinstance(resp_model, LinePayResponse)
        return resp_model

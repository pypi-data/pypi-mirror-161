from typing import Any, Dict

from requests import Response

from fastel.utils import requests


def api_token(sf_url: str, app_key: str, secret: str) -> str:
    url = sf_url + f"/openapi/api/token?appKey={app_key}&appSecret={secret}"
    resp: Response = requests.get(url)
    result = resp.json()
    if result["apiResultCode"] != 0:
        return ""
    result_data: Dict[str, Any] = result["apiResultData"]
    return result_data.get("accessToken", "")

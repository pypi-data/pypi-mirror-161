from typing import Any, Dict, List

from fastel.config import SdkConfig
from fastel.utils import requests


def validation_request(issuer: str, identity: str) -> Dict[str, Any]:
    url = f"{SdkConfig.auth_host}/validation/request?client_id={SdkConfig.client_id}&client_secret={SdkConfig.client_secret}&issuer={issuer}"
    result = requests.post(
        url,
        json={"identity": identity},
    ).json()
    assert isinstance(result, dict)
    return result


def validation_confirm(validation_id: str, code: str) -> Dict[str, Any]:
    url = f"{SdkConfig.auth_host}/validation/confirm/{validation_id}/{code}?client_id={SdkConfig.client_id}"
    result = requests.post(url, json={}).json()
    assert isinstance(result, dict)
    return result


def gen_token_request(
    identity: str, groups: List[str] = [], extra: Dict[str, Any] = {}
) -> Dict[str, Any]:
    url = f"{SdkConfig.auth_host}/jwt/server/encode?client_id={SdkConfig.client_id}&client_secret={SdkConfig.client_secret}"
    result = requests.post(
        url,
        json={"id": identity, "groups": groups, "ext": extra},
    ).json()
    assert isinstance(result, dict)
    return result


def revoke_token_request(identity: str) -> Dict[str, Any]:
    url = f"{SdkConfig.auth_host}/jwt/revoke?client_id={SdkConfig.client_id}&client_secret={SdkConfig.client_secret}"
    result = requests.post(url, json={"sub": identity}).json()
    assert isinstance(result, dict)
    return result

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from django.conf import settings


@dataclass
class BNetToken:
    access_token: str
    token_type: str


def fetch_client_credentials_token() -> BNetToken:
    client_id = settings.BNET_CLIENT_ID
    client_secret = settings.BNET_CLIENT_SECRET
    if not client_id or not client_secret:
        msg = "Client ID e/ou client secret não encontrado"
        raise RuntimeError(msg)

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    with httpx.Client(timeout=30.0) as client:
        res = client.post(settings.BNET_TOKEN_URL, data=data)
        res.raise_for_status()
        body = res.json()

    return BNetToken(
        access_token=body["access_token"], token_type=body.get("token_type", "bearer")
    )


def fetch_playable_race_index(
    *, namespace: str = "static-us", locale: str = "pt_BR"
) -> dict[str, Any]:
    token = fetch_client_credentials_token()
    url = f"{settings.BNET_API_BASE}/data/wow/playable-race/index"
    params = {"namespace": namespace, "locale": locale}
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=30.0) as client:
        res = client.get(url, params=params, headers=headers)
        res.raise_for_status()
        return res.json()


def fetch_playable_race_detail(
    race_id: int, *, namespace: str = "static-us", locale: str = "pt_BR"
) -> dict[str, Any]:
    token = fetch_client_credentials_token()
    url = f"{settings.BNET_API_BASE}/data/wow/playable-race/{race_id}"
    params = {"namespace": namespace, "locale": locale}
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=30.0) as client:
        res = client.get(url, params=params, headers=headers)
        res.raise_for_status()
        return res.json()


def fetch_playable_class_media(
    class_id: int, *, namespace: str = "static-us", locale: str = "pt_BR"
) -> dict[str, Any]:
    token = fetch_client_credentials_token()
    url = f"{settings.BNET_API_BASE}/data/wow/media/playable-class/{class_id}"
    params = {"namespace": namespace, "locale": locale}
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=30.0) as client:
        res = client.get(url, params=params, headers=headers)
        res.raise_for_status()
        return res.json()


def fetch_playable_class_index(
    *, namespace: str = "static-us", locale: str = "pt_BR"
) -> dict[str, Any]:
    token = fetch_client_credentials_token()
    url = f"{settings.BNET_API_BASE}/data/wow/playable-class/index"
    params = {"namespace": namespace, "locale": locale}
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=30.0) as client:
        res = client.get(url, params=params, headers=headers)
        res.raise_for_status()
        return res.json()


def fetch_playable_class_detail(
    class_id: int, *, namespace: str = "static-us", locale: str = "pt_BR"
) -> dict[str, Any]:
    token = fetch_client_credentials_token()
    url = f"{settings.BNET_API_BASE}/data/wow/playable-class/{class_id}"
    params = {"namespace": namespace, "locale": locale}
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=30.0) as client:
        res = client.get(url, params=params, headers=headers)
        res.raise_for_status()
        return res.json()


def fetch_playable_specialization_media(
    spec_id: int, *, namespace: str = "static-us", locale: str = "en_US"
) -> dict[str, Any]:
    token = fetch_client_credentials_token()
    url = f"{settings.BNET_API_BASE}/data/wow/media/playable-specialization/{spec_id}"
    params = {"namespace": namespace, "locale": locale}
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=30.0) as client:
        res = client.get(url, params=params, headers=headers)
        res.raise_for_status()
        return res.json()

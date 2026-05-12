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

from __future__ import annotations

from typing import Any

import httpx
from django.conf import settings
from django.db import transaction

from .client import fetch_client_credentials_token
from .models import PlayableRace


def _faction_label(detail: dict[str, Any], *, locale: str) -> str:
    faction = detail.get("faction") or {}
    names = faction.get("name")
    if isinstance(names, dict):
        short = locale.split("_")[0]
        return (
            names.get(locale)
            or names.get("pt_BR")
            or names.get("en_US")
            or names.get(short)
            or str(faction.get("type", ""))
        )
    return str(faction.get("type", ""))


def sync_playable_races_from_api(
    *, namespace: str = "static-us", locale: str = "pt_BR"
) -> int:
    token = fetch_client_credentials_token()
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    index_url = f"{settings.BNET_API_BASE}/data/wow/playable-race/index"
    params = {"namespace": namespace, "locale": locale}
    count = 0

    with httpx.Client(timeout=60.0) as client:
        idx = client.get(index_url, params=params, headers=headers)
        idx.raise_for_status()
        races = idx.json().get("races", [])

        with transaction.atomic():
            for race in races:
                href = race["key"]["href"]
                detail_res = client.get(
                    href, params={"locale": locale}, headers=headers
                )
                detail_res.raise_for_status()
                detail = detail_res.json()
                faction = _faction_label(detail, locale=locale)

                PlayableRace.objects.update_or_create(
                    blizzard_id=race["id"],
                    defaults={
                        "name": race["name"],
                        "faction": faction,
                    },
                )
                count += 1

    return count

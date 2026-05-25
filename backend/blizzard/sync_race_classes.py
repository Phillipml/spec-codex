from __future__ import annotations
from typing import Any
import httpx
from django.conf import settings
from django.db import transaction
from .client import fetch_client_credentials_token
from .models import PlayableRace, PlayableRaceClass
from .sync_races import _faction_label

# Aventureiro (14): listado na API mas sem media e fora do criador de personagem padrão.
_SKIP_CLASS_IDS = frozenset({14})


def _class_icon_url(media_payload: dict[str, Any]) -> str:
    for asset in media_payload.get("assets", []):
        if asset.get("key") == "icon":
            value = asset.get("value")
            if value:
                return str(value)
    return ""


def sync_playable_race_classes_from_api(
    race_id: int,
    *,
    namespace: str = "static-us",
    locale: str = "pt_BR",
    client: httpx.Client | None = None,
) -> int:
    owns_client = client is None
    if owns_client:
        client = httpx.Client(timeout=60.0)

    token = fetch_client_credentials_token()
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    params = {"namespace": namespace, "locale": locale}
    detail_url = f"{settings.BNET_API_BASE}/data/wow/playable-race/{race_id}"

    try:
        detail_res = client.get(detail_url, params=params, headers=headers)
        detail_res.raise_for_status()
        detail = detail_res.json()
        race, _ = PlayableRace.objects.update_or_create(
            race_id=detail["id"],
            defaults={
                "name": detail["name"],
                "faction": _faction_label(detail, locale=locale),
            },
        )
        playable_classes = detail.get("playable_classes", [])
        synced_class_ids: list[int] = []

        with transaction.atomic():
            for pc in playable_classes:
                class_id = int(pc["id"])
                if class_id in _SKIP_CLASS_IDS:
                    continue
                media_url = (
                    f"{settings.BNET_API_BASE}/data/wow/media/playable-class/{class_id}"
                )
                media_res = client.get(media_url, params=params, headers=headers)
                media_res.raise_for_status()
                icon_url = _class_icon_url(media_res.json())

                PlayableRaceClass.objects.update_or_create(
                    race=race,
                    class_id=class_id,
                    defaults={
                        "name": pc["name"],
                        "image_url": icon_url,
                    },
                )
                synced_class_ids.append(class_id)
            PlayableRaceClass.objects.filter(race=race).exclude(
                class_id__in=synced_class_ids
            ).delete()
        return len(synced_class_ids)
    finally:
        if owns_client:
            client.close()


def sync_all_playable_race_classes_from_api(
    *,
    namespace: str = "static-us",
    locale: str = "pt_BR",
) -> dict[str, int]:
    race_ids = list(
        PlayableRace.objects.order_by("race_id").values_list("race_id", flat=True)
    )
    if not race_ids:
        return {"races": 0, "classes": 0}
    total_classes = 0
    with httpx.Client(timeout=120.0) as client:
        for race_id in race_ids:
            n = sync_playable_race_classes_from_api(
                race_id,
                namespace=namespace,
                locale=locale,
                client=client,
            )
            total_classes += n
    return {"races": len(race_ids), "classes": total_classes}

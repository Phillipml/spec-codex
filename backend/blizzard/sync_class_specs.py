from __future__ import annotations

from typing import Any

import httpx
from django.conf import settings
from django.db import transaction

from .client import fetch_client_credentials_token
from .models import PlayableClass, PlayableClassSpecialization

_SKIP_CLASS_IDS = frozenset({14})


def _icon_url_from_media(media_payload: dict[str, Any]) -> str:
    for asset in media_payload.get("assets", []):
        if asset.get("key") == "icon":
            value = asset.get("value")
            if value:
                return str(value)
    return ""


def sync_playable_class_specs_from_api(
    class_id: int,
    *,
    namespace: str = "static-us",
    locale: str = "pt_BR",
    spec_media_locale: str = "en_US",
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
    spec_media_params = {"namespace": namespace, "locale": spec_media_locale}
    detail_url = f"{settings.BNET_API_BASE}/data/wow/playable-class/{class_id}"
    class_media_url = (
        f"{settings.BNET_API_BASE}/data/wow/media/playable-class/{class_id}"
    )

    try:
        detail_res = client.get(detail_url, params=params, headers=headers)
        detail_res.raise_for_status()
        detail = detail_res.json()

        media_res = client.get(class_media_url, params=params, headers=headers)
        media_res.raise_for_status()
        class_icon = _icon_url_from_media(media_res.json())

        specializations = detail.get("specializations", [])
        synced_spec_ids: list[int] = []

        with transaction.atomic():
            playable_class, _ = PlayableClass.objects.update_or_create(
                class_id=detail["id"],
                defaults={
                    "name": detail["name"],
                    "image_url": class_icon,
                },
            )

            for spec in specializations:
                spec_id = int(spec["id"])
                spec_media_url = f"{settings.BNET_API_BASE}/data/wow/media/playable-specialization/{spec_id}"
                spec_media_res = client.get(
                    spec_media_url,
                    params=spec_media_params,
                    headers=headers,
                )
                spec_media_res.raise_for_status()
                spec_icon = _icon_url_from_media(spec_media_res.json())
                PlayableClassSpecialization.objects.update_or_create(
                    playable_class=playable_class,
                    spec_id=spec_id,
                    defaults={
                        "name": spec["name"],
                        "image_url": spec_icon,
                    },
                )
                synced_spec_ids.append(spec_id)
            PlayableClassSpecialization.objects.filter(
                playable_class=playable_class
            ).exclude(spec_id__in=synced_spec_ids).delete()

        return len(synced_spec_ids)

    finally:
        if owns_client:
            client.close()


def sync_all_playable_class_specs_from_api(
    *,
    namespace: str = "static-us",
    locale: str = "pt_BR",
    spec_media_locale: str = "en_US",
) -> dict[str, int]:
    token = fetch_client_credentials_token()
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    params = {"namespace": namespace, "locale": locale}
    index_url = f"{settings.BNET_API_BASE}/data/wow/playable-class/index"
    total_specs = 0
    class_count = 0
    with httpx.Client(timeout=120.0) as client:
        index_res = client.get(index_url, params=params, headers=headers)
        index_res.raise_for_status()
        classes = index_res.json().get("classes", [])
        for item in classes:
            class_id = int(item["id"])
            if class_id in _SKIP_CLASS_IDS:
                continue
            n = sync_playable_class_specs_from_api(
                class_id,
                namespace=namespace,
                locale=locale,
                spec_media_locale=spec_media_locale,
                client=client,
            )
            total_specs += n
            class_count += 1
    return {"classes": class_count, "specializations": total_specs}

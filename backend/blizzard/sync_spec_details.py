from __future__ import annotations

from typing import Any

import httpx
from django.conf import settings
from django.db import transaction

from .client import fetch_client_credentials_token, get_with_retry
from .models import (
    PlayableClass,
    PlayableClassSpecialization,
    PlayableClassSpecializationSkill,
)

_SKIP_CLASS_IDS = frozenset({14})


def _icon_url_from_media(media_payload: dict[str, Any]) -> str:
    for asset in media_payload.get("assets", []):
        if asset.get("key") == "icon":
            value = asset.get("value")
            if value:
                return str(value)
    return ""


def _build_skill_payload(pvp_item: dict[str, Any]) -> dict[str, Any]:
    talent = pvp_item.get("talent") or {}
    tooltip = pvp_item.get("spell_tooltip") or {}
    skill: dict[str, Any] = {
        "skill_id": int(talent["id"]),
        "name": str(talent.get("name", "")),
        "description": str(tooltip.get("description", "")),
        "cast_time": str(tooltip.get("cast_time", "")),
        "power_cost": str(tooltip.get("power_cost", "")),
        "range": str(tooltip.get("range", "")),
        "cooldown": str(tooltip.get("cooldown", "")),
    }
    return skill


def _fetch_spell_icon(
    client: httpx.Client,
    *,
    pvp_talent_id: int,
    headers: dict[str, str],
    params: dict[str, str],
    spell_media_params: dict[str, str],
) -> str:
    pvp_url = f"{settings.BNET_API_BASE}/data/wow/pvp-talent/{pvp_talent_id}"
    pvp_res = get_with_retry(client, pvp_url, params=params, headers=headers)
    pvp_detail = pvp_res.json()

    spell = pvp_detail.get("spell") or {}
    spell_id = spell.get("id")
    if not spell_id:
        return ""

    spell_media_url = f"{settings.BNET_API_BASE}/data/wow/media/spell/{spell_id}"
    media_res = get_with_retry(
        client, spell_media_url, params=spell_media_params, headers=headers
    )
    media_res.raise_for_status()
    return _icon_url_from_media(media_res.json())


def sync_playable_spec_detail_from_api(
    spec_id: int,
    *,
    namespace: str = "static-us",
    locale: str = "pt_BR",
    spec_media_locale: str = "en_US",
    spell_media_locale: str = "en_US",
    client: httpx.Client | None = None,
) -> int:
    owns_client = client is None
    if owns_client:
        client = httpx.Client(timeout=120.0)

    token = fetch_client_credentials_token()
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    params = {"namespace": namespace, "locale": locale}
    spec_media_params = {"namespace": namespace, "locale": spec_media_locale}
    spell_media_params = {"namespace": namespace, "locale": spell_media_locale}

    detail_url = f"{settings.BNET_API_BASE}/data/wow/playable-specialization/{spec_id}"
    media_url = (
        f"{settings.BNET_API_BASE}/data/wow/media/playable-specialization/{spec_id}"
    )

    try:
        detail_res = get_with_retry(client, detail_url, params=params, headers=headers)
        detail = detail_res.json()

        playable_class_data = detail.get("playable_class") or {}
        class_id = int(playable_class_data["id"])
        if class_id in _SKIP_CLASS_IDS:
            return 0

        media_res = get_with_retry(
            client, media_url, params=spec_media_params, headers=headers
        )
        spec_icon = _icon_url_from_media(media_res.json())

        gender_desc = detail.get("gender_description") or {}
        description = str(gender_desc.get("male") or gender_desc.get("female") or "")

        role = detail.get("role") or {}
        role_name = str(role.get("name", ""))

        pvp_talents = detail.get("pvp_talents") or []
        skills_data: list[dict[str, Any]] = []

        for pvp_item in pvp_talents:
            skill = _build_skill_payload(pvp_item)
            skill["image_url"] = _fetch_spell_icon(
                client,
                pvp_talent_id=skill["skill_id"],
                headers=headers,
                params=params,
                spell_media_params=spell_media_params,
            )
            skills_data.append(skill)

        with transaction.atomic():
            playable_class, _ = PlayableClass.objects.update_or_create(
                class_id=class_id,
                defaults={"name": playable_class_data.get("name", "")},
            )

            specialization, _ = PlayableClassSpecialization.objects.update_or_create(
                playable_class=playable_class,
                spec_id=spec_id,
                defaults={
                    "name": detail.get("name", ""),
                    "image_url": spec_icon,
                    "description": description,
                    "role_name": role_name,
                },
            )

            synced_skill_ids: list[int] = []
            for skill in skills_data:
                PlayableClassSpecializationSkill.objects.update_or_create(
                    specialization=specialization,
                    skill_id=skill["skill_id"],
                    defaults={
                        "name": skill["name"],
                        "image_url": skill["image_url"],
                        "description": skill["description"],
                        "cast_time": skill["cast_time"],
                        "power_cost": skill["power_cost"],
                        "range": skill["range"],
                        "cooldown": skill["cooldown"],
                    },
                )
                synced_skill_ids.append(skill["skill_id"])

            PlayableClassSpecializationSkill.objects.filter(
                specialization=specialization
            ).exclude(skill_id__in=synced_skill_ids).delete()

        return len(skills_data)

    finally:
        if owns_client:
            client.close()


def sync_all_playable_spec_details_from_api(
    *,
    namespace: str = "static-us",
    locale: str = "pt_BR",
    spec_media_locale: str = "en_US",
    spell_media_locale: str = "en_US",
) -> dict[str, int]:
    token = fetch_client_credentials_token()
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
    }
    params = {"namespace": namespace, "locale": locale}
    index_url = f"{settings.BNET_API_BASE}/data/wow/playable-specialization/index"

    total_specs = 0
    total_skills = 0

    with httpx.Client(timeout=180.0) as client:
        index_res = get_with_retry(client, index_url, params=params, headers=headers)
        specs = index_res.json().get("character_specializations", [])

        for item in specs:
            spec_id = int(item["id"])
            n_skills = sync_playable_spec_detail_from_api(
                spec_id,
                namespace=namespace,
                locale=locale,
                spec_media_locale=spec_media_locale,
                spell_media_locale=spell_media_locale,
                client=client,
            )
            total_specs += 1
            total_skills += n_skills

    return {"specializations": total_specs, "skills": total_skills}

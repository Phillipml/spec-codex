from unittest.mock import MagicMock, patch

import pytest

from blizzard.client import BNetToken
from blizzard.models import (
    PlayableClass,
    PlayableClassSpecialization,
    PlayableClassSpecializationSkill,
)
from blizzard.sync_spec_details import (
    _build_skill_payload,
    _fetch_spell_icon,
    _icon_url_from_media,
    sync_all_playable_spec_details_from_api,
    sync_playable_spec_detail_from_api,
)

pytestmark = pytest.mark.django_db


class TestHelpers:
    def test_build_skill_payload(self):
        pvp_item = {
            "talent": {"id": 10, "name": "Golpe"},
            "spell_tooltip": {
                "description": "Dano",
                "cast_time": "Instant",
                "power_cost": "10",
                "range": "Melee",
                "cooldown": "6s",
            },
        }
        skill = _build_skill_payload(pvp_item)
        assert skill["skill_id"] == 10
        assert skill["name"] == "Golpe"
        assert skill["cooldown"] == "6s"

    def test_icon_url_from_media(self):
        assert _icon_url_from_media({"assets": []}) == ""

    def test_fetch_spell_icon_no_spell_id(self):
        client = MagicMock()
        client.get = MagicMock()
        with patch("blizzard.sync_spec_details.get_with_retry") as mock_retry:
            mock_retry.return_value = MagicMock(json=lambda: {"spell": {}})
            assert (
                _fetch_spell_icon(
                    client,
                    pvp_talent_id=1,
                    headers={},
                    params={},
                    spell_media_params={},
                )
                == ""
            )

    def test_fetch_spell_icon_with_spell(self):
        client = MagicMock()
        pvp_res = MagicMock(json=lambda: {"spell": {"id": 55}})
        media_res = MagicMock(
            json=lambda: {"assets": [{"key": "icon", "value": "https://spell"}]}
        )

        with patch(
            "blizzard.sync_spec_details.get_with_retry",
            side_effect=[pvp_res, media_res],
        ):
            url = _fetch_spell_icon(
                client,
                pvp_talent_id=1,
                headers={},
                params={},
                spell_media_params={},
            )
        assert url == "https://spell"


class TestSyncPlayableSpecDetailFromApi:
    @patch("blizzard.sync_spec_details.fetch_client_credentials_token")
    @patch("blizzard.sync_spec_details._fetch_spell_icon", return_value="https://icon")
    def test_sync_detail(self, mock_icon, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")

        detail = {
            "id": 71,
            "name": "Armas",
            "playable_class": {"id": 1, "name": "Guerreiro"},
            "gender_description": {"male": "Desc masculina"},
            "role": {"name": "Dano"},
            "pvp_talents": [
                {
                    "talent": {"id": 100, "name": "Golpe"},
                    "spell_tooltip": {"description": "Dano forte"},
                }
            ],
        }
        media = {"assets": [{"key": "icon", "value": "https://spec.png"}]}

        with patch("blizzard.sync_spec_details.get_with_retry") as mock_retry:
            mock_retry.side_effect = [
                MagicMock(json=lambda: detail),
                MagicMock(json=lambda: media),
            ]
            n = sync_playable_spec_detail_from_api(71)

        assert n == 1
        spec = PlayableClassSpecialization.objects.get(spec_id=71)
        assert spec.description == "Desc masculina"
        assert spec.role_name == "Dano"
        skill = PlayableClassSpecializationSkill.objects.get(specialization=spec)
        assert skill.name == "Golpe"
        assert skill.image_url == "https://icon"

    @patch("blizzard.sync_spec_details.fetch_client_credentials_token")
    def test_skips_adventurer_class(self, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")
        detail = {
            "id": 1,
            "name": "X",
            "playable_class": {"id": 14, "name": "Aventureiro"},
            "gender_description": {},
            "role": {},
            "pvp_talents": [],
        }
        with patch(
            "blizzard.sync_spec_details.get_with_retry",
            return_value=MagicMock(json=lambda: detail),
        ):
            assert sync_playable_spec_detail_from_api(1) == 0

    @patch("blizzard.sync_spec_details.fetch_client_credentials_token")
    def test_removes_stale_skills(self, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")
        pc = PlayableClass.objects.create(
            class_id=1, name="Guerreiro", image_url="https://c"
        )
        spec = PlayableClassSpecialization.objects.create(
            playable_class=pc,
            spec_id=71,
            name="Armas",
            image_url="https://s",
        )
        PlayableClassSpecializationSkill.objects.create(
            specialization=spec, skill_id=999, name="Old"
        )

        detail = {
            "id": 71,
            "name": "Armas",
            "playable_class": {"id": 1, "name": "Guerreiro"},
            "gender_description": {"female": "Desc"},
            "role": {"name": "Dano"},
            "pvp_talents": [
                {
                    "talent": {"id": 100, "name": "Novo"},
                    "spell_tooltip": {},
                }
            ],
        }
        media = {"assets": []}

        with patch("blizzard.sync_spec_details.get_with_retry") as mock_retry:
            mock_retry.side_effect = [
                MagicMock(json=lambda: detail),
                MagicMock(json=lambda: media),
            ]
            with patch("blizzard.sync_spec_details._fetch_spell_icon", return_value=""):
                sync_playable_spec_detail_from_api(71)

        assert not PlayableClassSpecializationSkill.objects.filter(
            skill_id=999
        ).exists()


class TestSyncAllPlayableSpecDetailsFromApi:
    @patch("blizzard.sync_spec_details.fetch_client_credentials_token")
    @patch(
        "blizzard.sync_spec_details.sync_playable_spec_detail_from_api", return_value=3
    )
    def test_sync_all(self, mock_single, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")
        index = {"character_specializations": [{"id": 71}, {"id": 72}]}

        with patch("blizzard.sync_spec_details.get_with_retry") as mock_retry:
            mock_retry.return_value = MagicMock(json=lambda: index)
            with patch("blizzard.sync_spec_details.httpx.Client") as client_cls:
                client = MagicMock()
                client.__enter__ = MagicMock(return_value=client)
                client.__exit__ = MagicMock(return_value=False)
                client_cls.return_value = client
                stats = sync_all_playable_spec_details_from_api()

        assert stats == {"specializations": 2, "skills": 6}

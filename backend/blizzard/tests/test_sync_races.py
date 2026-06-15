from unittest.mock import MagicMock, patch

import pytest

from blizzard.client import BNetToken
from blizzard.models import PlayableRace
from blizzard.sync_races import _faction_label, sync_playable_races_from_api

pytestmark = pytest.mark.django_db


class TestFactionLabel:
    def test_string_name(self):
        detail = {"faction": {"name": "Aliança"}}
        assert _faction_label(detail, locale="pt_BR") == "Aliança"

    def test_dict_name_locale_priority(self):
        detail = {
            "faction": {
                "name": {"pt_BR": "Horda", "en_US": "Horde"},
            }
        }
        assert _faction_label(detail, locale="pt_BR") == "Horda"

    def test_dict_name_fallback_en(self):
        detail = {"faction": {"name": {"en_US": "Horde"}}}
        assert _faction_label(detail, locale="pt_BR") == "Horde"

    def test_faction_type_mapping(self):
        detail = {"faction": {"type": "ALLIANCE"}}
        assert _faction_label(detail, locale="pt_BR") == "Aliança"

    def test_unknown_faction_type(self):
        detail = {"faction": {"type": "CUSTOM"}}
        assert _faction_label(detail, locale="pt_BR") == "CUSTOM"


class TestSyncPlayableRacesFromApi:
    @patch("blizzard.sync_races.fetch_client_credentials_token")
    def test_sync_creates_races(self, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")

        index_body = {
            "races": [
                {
                    "id": 1,
                    "name": "Humano",
                    "key": {"href": "https://api/race/1"},
                }
            ]
        }
        detail_body = {
            "id": 1,
            "name": "Humano",
            "faction": {"type": "ALLIANCE"},
        }

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def get(self, url, params=None, headers=None):
                res = MagicMock()
                if "index" in url:
                    res.json.return_value = index_body
                else:
                    res.json.return_value = detail_body
                return res

        with patch("blizzard.sync_races.httpx.Client", FakeClient):
            count = sync_playable_races_from_api()

        assert count == 1
        race = PlayableRace.objects.get(race_id=1)
        assert race.name == "Humano"
        assert race.faction == "Aliança"

from unittest.mock import MagicMock, patch

import httpx
import pytest

from blizzard.client import BNetToken
from blizzard.models import PlayableRace, PlayableRaceClass
from blizzard.sync_race_classes import (
    _class_icon_url,
    sync_all_playable_race_classes_from_api,
    sync_playable_race_classes_from_api,
)

pytestmark = pytest.mark.django_db


class TestClassIconUrl:
    def test_returns_icon(self):
        payload = {"assets": [{"key": "icon", "value": "https://x/icon.png"}]}
        assert _class_icon_url(payload) == "https://x/icon.png"

    def test_empty_when_missing(self):
        assert _class_icon_url({}) == ""
        assert _class_icon_url({"assets": [{"key": "other", "value": "x"}]}) == ""


class TestSyncPlayableRaceClassesFromApi:
    @patch("blizzard.sync_race_classes.fetch_client_credentials_token")
    def test_sync_race_classes(self, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")
        PlayableRace.objects.create(race_id=1, name="Humano", faction="Aliança")

        detail = {
            "id": 1,
            "name": "Humano",
            "faction": {"type": "ALLIANCE"},
            "playable_classes": [
                {"id": 1, "name": "Guerreiro"},
                {"id": 14, "name": "Aventureiro"},
            ],
        }
        media = {"assets": [{"key": "icon", "value": "https://x/warrior.png"}]}

        client = MagicMock()

        def fake_get(url, params=None, headers=None):
            res = MagicMock()
            if "/playable-race/" in url:
                res.json.return_value = detail
            else:
                res.json.return_value = media
            return res

        client.get.side_effect = fake_get

        count = sync_playable_race_classes_from_api(1, client=client)
        assert count == 1
        assert PlayableRaceClass.objects.filter(race__race_id=1).count() == 1
        rc = PlayableRaceClass.objects.get(race__race_id=1, class_id=1)
        assert rc.image_url == "https://x/warrior.png"

    @patch("blizzard.sync_race_classes.fetch_client_credentials_token")
    def test_removes_stale_classes(self, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")
        race = PlayableRace.objects.create(race_id=1, name="Humano", faction="Aliança")
        PlayableRaceClass.objects.create(
            race=race, class_id=99, name="Old", image_url="https://old"
        )

        detail = {
            "id": 1,
            "name": "Humano",
            "faction": {"name": "Aliança"},
            "playable_classes": [{"id": 1, "name": "Guerreiro"}],
        }
        media = {"assets": [{"key": "icon", "value": "https://x/w.png"}]}
        client = MagicMock()

        def fake_get(url, params=None, headers=None):
            res = MagicMock()
            res.json.return_value = detail if "playable-race" in url else media
            return res

        client.get.side_effect = fake_get
        sync_playable_race_classes_from_api(1, client=client)
        assert not PlayableRaceClass.objects.filter(class_id=99).exists()

    @patch("blizzard.sync_race_classes.fetch_client_credentials_token")
    def test_owns_client_lifecycle(self, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")

        detail = {
            "id": 1,
            "name": "Humano",
            "faction": {"name": "Aliança"},
            "playable_classes": [],
        }

        class FakeClient:
            def __init__(self, *args, **kwargs):
                self.closed = False

            def get(self, url, params=None, headers=None):
                res = MagicMock()
                res.json.return_value = detail
                return res

            def close(self):
                self.closed = True

        instances: list[FakeClient] = []

        def factory(*args, **kwargs):
            c = FakeClient()
            instances.append(c)
            return c

        with patch("blizzard.sync_race_classes.httpx.Client", factory):
            sync_playable_race_classes_from_api(1)

        assert len(instances) == 1
        assert instances[0].closed is True


class TestSyncAllPlayableRaceClassesFromApi:
    def test_empty_races(self):
        stats = sync_all_playable_race_classes_from_api()
        assert stats == {"races": 0, "classes": 0}

    @patch(
        "blizzard.sync_race_classes.sync_playable_race_classes_from_api", return_value=2
    )
    def test_with_races(self, mock_sync):
        PlayableRace.objects.create(race_id=1, name="Humano", faction="Aliança")
        PlayableRace.objects.create(race_id=2, name="Orc", faction="Horda")
        stats = sync_all_playable_race_classes_from_api()
        assert stats == {"races": 2, "classes": 4}

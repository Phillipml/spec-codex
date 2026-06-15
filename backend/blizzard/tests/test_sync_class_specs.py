from unittest.mock import MagicMock, patch

import pytest

from blizzard.client import BNetToken
from blizzard.models import PlayableClass, PlayableClassSpecialization
from blizzard.sync_class_specs import (
    _icon_url_from_media,
    sync_all_playable_class_specs_from_api,
    sync_playable_class_specs_from_api,
)

pytestmark = pytest.mark.django_db


class TestIconUrlFromMedia:
    def test_icon_found(self):
        assert (
            _icon_url_from_media({"assets": [{"key": "icon", "value": "https://i"}]})
            == "https://i"
        )

    def test_icon_missing(self):
        assert _icon_url_from_media({}) == ""


class TestSyncPlayableClassSpecsFromApi:
    @patch("blizzard.sync_class_specs.fetch_client_credentials_token")
    def test_sync_specs(self, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")

        detail = {
            "id": 1,
            "name": "Guerreiro",
            "specializations": [{"id": 71, "name": "Armas"}],
        }
        class_media = {"assets": [{"key": "icon", "value": "https://c.png"}]}
        spec_media = {"assets": [{"key": "icon", "value": "https://s.png"}]}

        client = MagicMock()

        def fake_get(url, params=None, headers=None):
            res = MagicMock()
            if url.endswith("/playable-class/1") and "media" not in url:
                res.json.return_value = detail
            elif "media/playable-class" in url:
                res.json.return_value = class_media
            else:
                res.json.return_value = spec_media
            return res

        client.get.side_effect = fake_get
        n = sync_playable_class_specs_from_api(1, client=client)
        assert n == 1
        pc = PlayableClass.objects.get(class_id=1)
        spec = PlayableClassSpecialization.objects.get(playable_class=pc, spec_id=71)
        assert spec.image_url == "https://s.png"

    @patch("blizzard.sync_class_specs.fetch_client_credentials_token")
    def test_removes_stale_specs(self, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")
        pc = PlayableClass.objects.create(
            class_id=1, name="Guerreiro", image_url="https://c"
        )
        PlayableClassSpecialization.objects.create(
            playable_class=pc,
            spec_id=99,
            name="Old",
            image_url="https://old",
        )

        detail = {
            "id": 1,
            "name": "Guerreiro",
            "specializations": [{"id": 71, "name": "Armas"}],
        }
        media = {"assets": [{"key": "icon", "value": "https://x"}]}
        client = MagicMock()
        client.get.return_value = MagicMock()
        client.get.return_value.json.side_effect = [detail, media, media]

        sync_playable_class_specs_from_api(1, client=client)
        assert not PlayableClassSpecialization.objects.filter(spec_id=99).exists()


class TestSyncAllPlayableClassSpecsFromApi:
    @patch("blizzard.sync_class_specs.fetch_client_credentials_token")
    @patch(
        "blizzard.sync_class_specs.sync_playable_class_specs_from_api", return_value=2
    )
    def test_sync_all(self, mock_single, mock_token, settings):
        mock_token.return_value = BNetToken(access_token="tok", token_type="bearer")
        index = {"classes": [{"id": 1}, {"id": 14}, {"id": 2}]}

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def get(self, url, params=None, headers=None):
                res = MagicMock()
                res.json.return_value = index
                return res

        with patch("blizzard.sync_class_specs.httpx.Client", FakeClient):
            stats = sync_all_playable_class_specs_from_api()

        assert stats == {"classes": 2, "specializations": 4}
        assert mock_single.call_count == 2

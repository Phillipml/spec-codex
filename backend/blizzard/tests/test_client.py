from unittest.mock import MagicMock

import httpx
import pytest

from blizzard.client import BNetToken, get_with_retry

pytestmark = pytest.mark.django_db


class TestGetWithRetry:
    def test_success_first_attempt(self):
        client = MagicMock()
        response = MagicMock()
        response.status_code = 200
        client.get.return_value = response

        result = get_with_retry(client, "https://example.com")

        assert result is response
        response.raise_for_status.assert_called_once()

    def test_retries_on_retryable_status_then_succeeds(self, monkeypatch):
        client = MagicMock()
        bad = MagicMock(status_code=503)
        good = MagicMock(status_code=200)
        client.get.side_effect = [bad, good]
        sleeps: list[float] = []
        monkeypatch.setattr("blizzard.client.time.sleep", lambda s: sleeps.append(s))

        result = get_with_retry(client, "https://example.com", max_attempts=3)

        assert result is good
        assert client.get.call_count == 2
        assert sleeps == [1.0]

    def test_raises_after_exhausting_retryable_status(self, monkeypatch):
        client = MagicMock()
        response = MagicMock(status_code=502)
        client.get.return_value = response
        monkeypatch.setattr("blizzard.client.time.sleep", lambda _s: None)
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "err", request=MagicMock(), response=response
        )

        with pytest.raises(httpx.HTTPStatusError):
            get_with_retry(client, "https://example.com", max_attempts=2)

    def test_retries_on_connection_error(self, monkeypatch):
        client = MagicMock()
        good = MagicMock(status_code=200)
        client.get.side_effect = [httpx.ConnectError("down"), good]
        monkeypatch.setattr("blizzard.client.time.sleep", lambda _s: None)

        result = get_with_retry(client, "https://example.com", max_attempts=3)

        assert result is good

    def test_reraises_connection_error_after_max_attempts(self, monkeypatch):
        client = MagicMock()
        client.get.side_effect = httpx.ConnectError("down")
        monkeypatch.setattr("blizzard.client.time.sleep", lambda _s: None)

        with pytest.raises(httpx.ConnectError):
            get_with_retry(client, "https://example.com", max_attempts=2)


class TestFetchClientCredentialsToken:
    def test_missing_credentials_raises(self, settings):
        settings.BNET_CLIENT_ID = ""
        settings.BNET_CLIENT_SECRET = ""

        from blizzard.client import fetch_client_credentials_token

        with pytest.raises(RuntimeError, match="Client ID"):
            fetch_client_credentials_token()

    def test_success(self, settings, monkeypatch):
        settings.BNET_TOKEN_URL = "https://oauth.battle.net/token"

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def post(self, url, data):
                assert data["client_id"] == "test-client-id"
                res = MagicMock()
                res.json.return_value = {
                    "access_token": "tok123",
                    "token_type": "bearer",
                }
                return res

        monkeypatch.setattr("blizzard.client.httpx.Client", FakeClient)

        from blizzard.client import fetch_client_credentials_token

        token = fetch_client_credentials_token()
        assert token == BNetToken(access_token="tok123", token_type="bearer")


class TestFetchApiHelpers:
    def _patch_token_and_client(self, monkeypatch, json_body):
        monkeypatch.setattr(
            "blizzard.client.fetch_client_credentials_token",
            lambda: BNetToken(access_token="tok", token_type="bearer"),
        )

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def get(self, url, params=None, headers=None):
                res = MagicMock()
                res.json.return_value = json_body
                return res

        monkeypatch.setattr("blizzard.client.httpx.Client", FakeClient)

    @pytest.mark.parametrize(
        "func_name,args,expected_key",
        [
            ("fetch_playable_race_index", (), "races"),
            ("fetch_playable_race_detail", (1,), "id"),
            ("fetch_playable_class_media", (1,), "assets"),
            ("fetch_playable_class_index", (), "classes"),
            ("fetch_playable_class_detail", (1,), "id"),
            ("fetch_playable_specialization_media", (1,), "assets"),
            ("fetch_playable_specialization_index", (), "character_specializations"),
            ("fetch_playable_specialization_detail", (1,), "id"),
            ("fetch_pvp_talent_detail", (1,), "id"),
            ("fetch_spell_media", (1,), "assets"),
        ],
    )
    def test_fetch_functions(self, monkeypatch, func_name, args, expected_key):
        from blizzard import client as client_module

        body = {expected_key: [] if expected_key.endswith("s") else 1}
        if expected_key == "id":
            body = {"id": 1, "name": "x"}
        if expected_key == "assets":
            body = {"assets": [{"key": "icon", "value": "https://x"}]}
        self._patch_token_and_client(monkeypatch, body)
        fn = getattr(client_module, func_name)
        result = fn(*args)
        assert expected_key in result or result.get("id") == 1

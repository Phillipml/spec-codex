from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from blizzard.models import (
    PlayableClass,
    PlayableClassSpecialization,
    PlayableClassSpecializationSkill,
    PlayableRace,
    PlayableRaceClass,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def auth_headers():
    return {"HTTP_AUTHORIZATION": "Bearer test-cron-secret"}


@pytest.fixture
def sample_race():
    return PlayableRace.objects.create(race_id=1, name="Humano", faction="Aliança")


@pytest.fixture
def sample_class():
    return PlayableClass.objects.create(
        class_id=1, name="Guerreiro", image_url="https://example.com/c.png"
    )


class TestPlayableRaceListView:
    def test_list_races(self, api, sample_race):
        res = api.get("/api/playable-race/index")
        assert res.status_code == 200
        assert res.json() == [{"id": 1, "name": "Humano", "faction": "Aliança"}]


class TestPlayableRaceSyncView:
    def test_missing_cron_secret(self, api):
        with override_settings(CRON_SYNC_SECRET=""):
            res = api.post("/api/playable-race/sync")
        assert res.status_code == 503

    def test_missing_auth_header(self, api):
        res = api.post("/api/playable-race/sync")
        assert res.status_code == 401

    def test_invalid_token(self, api):
        res = api.post(
            "/api/playable-race/sync",
            HTTP_AUTHORIZATION="Bearer wrong",
        )
        assert res.status_code == 403

    @patch("blizzard.views.sync_playable_races_from_api", return_value=3)
    def test_success(self, mock_sync, api, auth_headers):
        res = api.post("/api/playable-race/sync", **auth_headers)
        assert res.status_code == 200
        assert res.json() == {"synced": 3}

    @patch(
        "blizzard.views.sync_playable_races_from_api",
        side_effect=RuntimeError("api down"),
    )
    def test_sync_error(self, mock_sync, api, auth_headers):
        res = api.post("/api/playable-race/sync", **auth_headers)
        assert res.status_code == 502
        assert res.json()["detail"] == "api down"


class TestPlayableRaceClassesListView:
    def test_race_not_found(self, api):
        res = api.get("/api/playable-race/99/playable-classes")
        assert res.status_code == 404

    def test_no_classes_synced(self, api, sample_race):
        res = api.get("/api/playable-race/1/playable-classes")
        assert res.status_code == 404

    def test_success(self, api, sample_race):
        PlayableRaceClass.objects.create(
            race=sample_race,
            class_id=1,
            name="Guerreiro",
            image_url="https://example.com/i.png",
        )
        res = api.get("/api/playable-race/1/playable-classes")
        assert res.status_code == 200
        data = res.json()
        assert data["race_name"] == "Humano"
        assert len(data["playable_classes"]) == 1


class TestPlayableRaceClassesSyncView:
    @patch(
        "blizzard.views.sync_all_playable_race_classes_from_api",
        return_value={"races": 2, "classes": 5},
    )
    def test_success(self, mock_sync, api, auth_headers):
        res = api.post("/api/playable-race/playable-classes/sync", **auth_headers)
        assert res.status_code == 200
        assert res.json() == {"races": 2, "classes": 5}

    @patch(
        "blizzard.views.sync_all_playable_race_classes_from_api",
        side_effect=Exception("fail"),
    )
    def test_error(self, mock_sync, api, auth_headers):
        res = api.post("/api/playable-race/playable-classes/sync", **auth_headers)
        assert res.status_code == 502


class TestPlayableRaceClassSpecsDetailView:
    def test_race_not_found(self, api):
        res = api.get("/api/playable-race/1/playable-classes/1/specs/")
        assert res.status_code == 404

    def test_class_not_available_for_race(self, api, sample_race, sample_class):
        res = api.get("/api/playable-race/1/playable-classes/1/specs/")
        assert res.status_code == 404

    def test_class_not_found(self, api, sample_race):
        PlayableRaceClass.objects.create(
            race=sample_race,
            class_id=1,
            name="Guerreiro",
            image_url="https://example.com/i.png",
        )
        res = api.get("/api/playable-race/1/playable-classes/1/specs/")
        assert res.status_code == 404
        assert "Classe não encontrada" in res.json()["detail"]

    def test_specs_not_synced(self, api, sample_race, sample_class):
        PlayableRaceClass.objects.create(
            race=sample_race,
            class_id=1,
            name="Guerreiro",
            image_url="https://example.com/i.png",
        )
        res = api.get("/api/playable-race/1/playable-classes/1/specs/")
        assert res.status_code == 404
        assert "Specs ainda não sincronizadas" in res.json()["detail"]

    def test_success(self, api, sample_race, sample_class):
        PlayableRaceClass.objects.create(
            race=sample_race,
            class_id=1,
            name="Guerreiro",
            image_url="https://example.com/i.png",
        )
        PlayableClassSpecialization.objects.create(
            playable_class=sample_class,
            spec_id=71,
            name="Armas",
            image_url="https://example.com/s.png",
        )
        res = api.get("/api/playable-race/1/playable-classes/1/specs/")
        assert res.status_code == 200
        assert res.json()["class"]["specializations"][0]["name"] == "Armas"


class TestPlayableClassSpecsListView:
    def test_empty(self, api):
        res = api.get("/api/playable-classes/specs")
        assert res.status_code == 404

    def test_success(self, api, sample_class):
        PlayableClassSpecialization.objects.create(
            playable_class=sample_class,
            spec_id=71,
            name="Armas",
            image_url="https://example.com/s.png",
        )
        res = api.get("/api/playable-classes/specs")
        assert res.status_code == 200
        assert res.json()[0]["name"] == "Guerreiro"


class TestPlayableClassSpecsSyncView:
    @patch(
        "blizzard.views.sync_all_playable_class_specs_from_api",
        return_value={"classes": 1, "specializations": 3},
    )
    def test_success(self, mock_sync, api, auth_headers):
        res = api.post("/api/playable-classes/specs/sync", **auth_headers)
        assert res.status_code == 200

    @patch(
        "blizzard.views.sync_all_playable_class_specs_from_api",
        side_effect=Exception("x"),
    )
    def test_error(self, mock_sync, api, auth_headers):
        res = api.post("/api/playable-classes/specs/sync", **auth_headers)
        assert res.status_code == 502


class TestPlayableRaceClassSpecDetailView:
    def test_race_not_found(self, api):
        res = api.get("/api/playable-race/1/playable-classes/1/specs/71/")
        assert res.status_code == 404

    def test_class_not_for_race(self, api, sample_race, sample_class):
        res = api.get("/api/playable-race/1/playable-classes/1/specs/71/")
        assert res.status_code == 404

    def test_spec_not_found(self, api, sample_race, sample_class):
        PlayableRaceClass.objects.create(
            race=sample_race,
            class_id=1,
            name="Guerreiro",
            image_url="https://example.com/i.png",
        )
        res = api.get("/api/playable-race/1/playable-classes/1/specs/71/")
        assert res.status_code == 404

    def test_details_not_synced(self, api, sample_race, sample_class):
        PlayableRaceClass.objects.create(
            race=sample_race,
            class_id=1,
            name="Guerreiro",
            image_url="https://example.com/i.png",
        )
        PlayableClassSpecialization.objects.create(
            playable_class=sample_class,
            spec_id=71,
            name="Armas",
            image_url="https://example.com/s.png",
        )
        res = api.get("/api/playable-race/1/playable-classes/1/specs/71/")
        assert res.status_code == 404
        assert "Detalhes da spec" in res.json()["detail"]

    def test_success_with_full_skill_payload(self, api, sample_race, sample_class):
        PlayableRaceClass.objects.create(
            race=sample_race,
            class_id=1,
            name="Guerreiro",
            image_url="https://example.com/i.png",
        )
        spec = PlayableClassSpecialization.objects.create(
            playable_class=sample_class,
            spec_id=71,
            name="Armas",
            image_url="https://example.com/s.png",
            description="Desc",
            role_name="Dano",
        )
        PlayableClassSpecializationSkill.objects.create(
            specialization=spec,
            skill_id=100,
            name="Golpe",
            image_url="https://example.com/sp.png",
            description="Dano",
            cast_time="Instantâneo",
            power_cost="10 Raiva",
            range="Corpo a corpo",
            cooldown="6 seg",
        )
        res = api.get("/api/playable-race/1/playable-classes/1/specs/71/")
        assert res.status_code == 200
        skill = res.json()["class"]["specialization"]["skills"][0]
        assert skill["power_cost"] == "10 Raiva"
        assert skill["range"] == "Corpo a corpo"
        assert skill["cooldown"] == "6 seg"


class TestPlayableClassSpecDetailsSyncView:
    @patch(
        "blizzard.views.sync_all_playable_spec_details_from_api",
        return_value={"specializations": 1, "skills": 4},
    )
    def test_success(self, mock_sync, api, auth_headers):
        res = api.post("/api/playable-classes/specs/details/sync", **auth_headers)
        assert res.status_code == 200
        assert res.json() == {"specializations": 1, "skills": 4}

    @patch(
        "blizzard.views.sync_all_playable_spec_details_from_api",
        side_effect=Exception("boom"),
    )
    def test_error(self, mock_sync, api, auth_headers):
        res = api.post("/api/playable-classes/specs/details/sync", **auth_headers)
        assert res.status_code == 502

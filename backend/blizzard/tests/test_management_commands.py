from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


class TestManagementCommands:
    @patch(
        "blizzard.management.commands.sync_playable_races.sync_playable_races_from_api",
        return_value=5,
    )
    def test_sync_playable_races(self, mock_sync):
        out = StringIO()
        call_command(
            "sync_playable_races", "--namespace=static-eu", "--locale=en_US", stdout=out
        )
        mock_sync.assert_called_once_with(namespace="static-eu", locale="en_US")
        assert "5" in out.getvalue()

    @patch(
        "blizzard.management.commands.sync_playable_race_classes.sync_all_playable_race_classes_from_api",
        return_value={"races": 2, "classes": 10},
    )
    def test_sync_playable_race_classes(self, mock_sync):
        out = StringIO()
        call_command("sync_playable_race_classes", stdout=out)
        assert "2" in out.getvalue()
        assert "10" in out.getvalue()

    @patch(
        "blizzard.management.commands.sync_playable_class_specs.sync_all_playable_class_specs_from_api",
        return_value={"classes": 3, "specializations": 9},
    )
    def test_sync_playable_class_specs(self, mock_sync):
        out = StringIO()
        call_command(
            "sync_playable_class_specs",
            "--namespace=static-us",
            "--locale=pt_BR",
            "--spec-media-locale=en_US",
            stdout=out,
        )
        mock_sync.assert_called_once_with(
            namespace="static-us",
            locale="pt_BR",
            spec_media_locale="en_US",
        )
        assert "9" in out.getvalue()

    @patch(
        "blizzard.management.commands.sync_playable_spec_details.sync_all_playable_spec_details_from_api",
        return_value={"specializations": 4, "skills": 20},
    )
    def test_sync_playable_spec_details(self, mock_sync):
        out = StringIO()
        call_command(
            "sync_playable_spec_details",
            "--namespace=static-us",
            "--locale=pt_BR",
            "--spec-media-locale=en_US",
            "--spell-media-locale=en_US",
            stdout=out,
        )
        mock_sync.assert_called_once_with(
            namespace="static-us",
            locale="pt_BR",
            spec_media_locale="en_US",
            spell_media_locale="en_US",
        )
        assert "20" in out.getvalue()

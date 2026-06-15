import pytest

from blizzard.models import (
    PlayableClass,
    PlayableClassSpecialization,
    PlayableClassSpecializationSkill,
    PlayableRace,
    PlayableRaceClass,
)

pytestmark = pytest.mark.django_db


def test_playable_race_str():
    race = PlayableRace.objects.create(race_id=1, name="Humano", faction="Aliança")
    assert str(race) == "Humano (1)"


def test_playable_race_class_str():
    race = PlayableRace.objects.create(race_id=1, name="Humano", faction="Aliança")
    rc = PlayableRaceClass.objects.create(
        race=race, class_id=1, name="Guerreiro", image_url="https://example.com/i.png"
    )
    assert str(rc) == "Humano - Guerreiro"


def test_playable_class_str():
    pc = PlayableClass.objects.create(
        class_id=1, name="Guerreiro", image_url="https://example.com/i.png"
    )
    assert str(pc) == "Guerreiro (1)"


def test_playable_class_specialization_str():
    pc = PlayableClass.objects.create(
        class_id=1, name="Guerreiro", image_url="https://example.com/i.png"
    )
    spec = PlayableClassSpecialization.objects.create(
        playable_class=pc,
        spec_id=71,
        name="Armas",
        image_url="https://example.com/s.png",
    )
    assert str(spec) == "Guerreiro - Armas"


def test_playable_class_specialization_skill_str():
    pc = PlayableClass.objects.create(
        class_id=1, name="Guerreiro", image_url="https://example.com/i.png"
    )
    spec = PlayableClassSpecialization.objects.create(
        playable_class=pc,
        spec_id=71,
        name="Armas",
        image_url="https://example.com/s.png",
    )
    skill = PlayableClassSpecializationSkill.objects.create(
        specialization=spec,
        skill_id=100,
        name="Golpe Heroico",
    )
    assert str(skill) == "Armas - Golpe Heroico"

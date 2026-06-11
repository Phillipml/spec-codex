from email.policy import default
from operator import length_hint
from tokenize import blank_re
from django.db import models


class PlayableRace(models.Model):
    race_id = models.PositiveIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    faction = models.CharField(max_length=255)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "playable_races"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.race_id})"


class PlayableRaceClass(models.Model):
    race = models.ForeignKey(
        PlayableRace,
        on_delete=models.CASCADE,
        related_name="playable_classes",
    )
    class_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=512)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "playable_race_classes"
        unique_together = [("race", "class_id")]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.race.name} - {self.name}"


class PlayableClass(models.Model):
    class_id = models.PositiveIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=512)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "playable_classes"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.class_id})"


class PlayableClassSpecialization(models.Model):
    playable_class = models.ForeignKey(
        PlayableClass,
        on_delete=models.CASCADE,
        related_name="specializations",
    )
    spec_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=512)
    description = models.TextField(blank=True, default="")
    role_name = models.CharField(max_length=64, blank=True, default="")
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "playable_class_specializations"
        unique_together = [("playable_class", "spec_id")]

    def __str__(self) -> str:
        return f"{self.playable_class.name} - {self.name}"


class PlayableClassSpecializationSkill(models.Model):
    specialization = models.ForeignKey(
        PlayableClassSpecialization,
        on_delete=models.CASCADE,
        related_name="skills",
    )
    skill_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=512, blank=True, default="")
    description = models.TextField(blank=True, default="")
    cast_time = models.CharField(max_length=128, blank=True, default="")
    power_cost = models.CharField(max_length=128, blank=True, default="")
    range = models.CharField(max_length=128, blank=True, default="")
    cooldown = models.CharField(max_length=128, blank=True, default="")
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "playable_class_specialization_skills"
        unique_together = [("specialization", "skill_id")]
        ordering = ["skill_id"]

    def __str__(self) -> str:
        return f"{self.specialization.name} - {self.name}"

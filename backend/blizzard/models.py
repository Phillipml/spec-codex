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

    class Meta:
        db_table = "playable_race_classes"
        unique_together = [("race", "class_id")]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.race.name} - {self.name}"

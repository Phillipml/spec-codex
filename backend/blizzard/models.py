from django.db import models


class PlayableRace(models.Model):
    race_id = models.PositiveIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    faction = models.CharField(max_length=255)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.race_id})"

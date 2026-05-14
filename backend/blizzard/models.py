from django.db import models


class PlayableRace(models.Model):
    race_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    faction = models.CharField(max_length=255)
    synced_at = models.DateTimeField(auto_now=True)

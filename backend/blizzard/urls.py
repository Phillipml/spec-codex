from django.urls import path

from .views import (
    PlayableRaceClassesListView,
    PlayableRaceClassesSyncView,
    PlayableRaceListView,
    PlayableRaceSyncView,
)

urlpatterns = [
    path(
        "wow/playable-race/index",
        PlayableRaceListView.as_view(),
        name="wow-playable-race-index",
    ),
    path(
        "wow/playable-race/sync",
        PlayableRaceSyncView.as_view(),
        name="wow-playable-race-sync",
    ),
    path(
        "wow/playable-race/<int:race_id>/playable-classes/index",
        PlayableRaceClassesListView.as_view(),
        name="wow-playable-race-classes-index",
    ),
    path(
        "wow/playable-race/playable-classes/sync",
        PlayableRaceClassesSyncView.as_view(),
        name="wow-playable-race-classes-sync",
    ),
]

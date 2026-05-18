from django.urls import path

from .views import PlayableRaceListView, PlayableRaceSyncView

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
]

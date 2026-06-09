from django.urls import path

from .views import (
    PlayableClassSpecsListView,
    PlayableClassSpecsSyncView,
    PlayableRaceClassSpecsDetailView,
    PlayableRaceClassesListView,
    PlayableRaceClassesSyncView,
    PlayableRaceListView,
    PlayableRaceSyncView,
)

urlpatterns = [
    path(
        "playable-race/index",
        PlayableRaceListView.as_view(),
        name="playable-race-index",
    ),
    path(
        "playable-race/sync",
        PlayableRaceSyncView.as_view(),
        name="playable-race-sync",
    ),
    path(
        "playable-race/playable-classes/sync",
        PlayableRaceClassesSyncView.as_view(),
        name="playable-race-classes-sync",
    ),
    path(
        "playable-race/<int:race_id>/playable-classes/<int:class_id>/specs/",
        PlayableRaceClassSpecsDetailView.as_view(),
        name="playable-race-class-specs",
    ),
    path(
        "playable-race/<int:race_id>/playable-classes",
        PlayableRaceClassesListView.as_view(),
        name="playable-race-classes",
    ),
    path(
        "playable-classes/specs",
        PlayableClassSpecsListView.as_view(),
        name="playable-class-specs",
    ),
    path(
        "playable-classes/specs/sync",
        PlayableClassSpecsSyncView.as_view(),
        name="playable-class-specs-sync",
    ),
]

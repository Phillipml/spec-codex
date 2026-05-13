from django.urls import path
from .views import PlayableRaceIndexView

urlpatterns = [
    path(
        "wow/playable-race/index",
        PlayableRaceIndexView.as_view(),
        name="wow-playable-race-index",
    ),
]

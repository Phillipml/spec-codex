from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .client import fetch_playable_race_index


class PlayableRaceIndexView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = fetch_playable_race_index()
        return Response(data)

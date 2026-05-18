import secrets

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PlayableRace
from .sync_races import sync_playable_races_from_api


class PlayableRaceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        rows = PlayableRace.objects.all()
        data = [{"id": r.race_id, "name": r.name, "faction": r.faction} for r in rows]
        return Response(data)


class PlayableRaceSyncView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        expected = settings.CRON_SYNC_SECRET
        if not expected:
            return Response(
                {"detail": "CRON_SYNC_SECRET não configurado."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        auth = request.headers.get("Authorization") or ""
        prefix = "Bearer "
        if not auth.startswith(prefix):
            return Response(
                {"detail": "Authorization Bearer obrigatório."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token = auth[len(prefix) :].strip()
        if not secrets.compare_digest(token, expected):
            return Response(
                {"detail": "Token inválido."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            n = sync_playable_races_from_api()
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"synced": n})

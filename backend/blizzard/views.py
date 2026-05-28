import secrets

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PlayableClass, PlayableRace
from .sync_class_specs import sync_all_playable_class_specs_from_api
from .sync_race_classes import sync_all_playable_race_classes_from_api
from .sync_races import sync_playable_races_from_api


def _cron_auth_response(request) -> Response | None:
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
    return None


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
        err = _cron_auth_response(request)
        if err is not None:
            return err

        try:
            n = sync_playable_races_from_api()
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"synced": n})


class PlayableRaceClassesListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, race_id: int):
        try:
            race = PlayableRace.objects.get(race_id=race_id)
        except PlayableRace.DoesNotExist:
            return Response(
                {"detail": "Raça não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        rows = race.playable_classes.all()
        if not rows.exists():
            return Response(
                {"detail": "Classes ainda não sincronizadas para esta raça."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": race.race_id,
                "race_id": race.race_id,
                "race_name": race.name,
                "faction": race.faction,
                "playable_classes": [
                    {
                        "class_id": c.class_id,
                        "name": c.name,
                        "image": c.image_url,
                    }
                    for c in rows
                ],
            }
        )


class PlayableRaceClassesSyncView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        err = _cron_auth_response(request)
        if err is not None:
            return err

        try:
            stats = sync_all_playable_race_classes_from_api()
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(stats)


class PlayableClassSpecsListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        rows = PlayableClass.objects.prefetch_related("specializations").all()
        if not rows.exists():
            return Response(
                {"detail": "Classes e specs ainda não sincronizadas."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = [
            {
                "id": c.class_id,
                "name": c.name,
                "image": c.image_url,
                "specializations": [
                    {
                        "id": s.spec_id,
                        "name": s.name,
                        "image": s.image_url,
                    }
                    for s in c.specializations.all()
                ],
            }
            for c in rows
        ]
        return Response(data)


class PlayableClassSpecsSyncView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        err = _cron_auth_response(request)
        if err is not None:
            return err

        try:
            stats = sync_all_playable_class_specs_from_api()
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(stats)

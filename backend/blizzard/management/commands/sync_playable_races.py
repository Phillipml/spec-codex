from django.core.management.base import BaseCommand

from blizzard.sync_races import sync_playable_races_from_api


class Command(BaseCommand):
    help = "Busca raças na Blizzard (índice + detalhe) e grava/atualiza no banco."

    def add_arguments(self, parser):
        parser.add_argument(
            "--namespace",
            default="static-us",
            help="Namespace da Game Data (ex.: static-us).",
        )
        parser.add_argument(
            "--locale",
            default="pt_BR",
            help="Locale (ex.: pt_BR).",
        )

    def handle(self, *args, **options):
        n = sync_playable_races_from_api(
            namespace=options["namespace"],
            locale=options["locale"],
        )
        self.stdout.write(self.style.SUCCESS(f"Sincronizadas {n} raças."))

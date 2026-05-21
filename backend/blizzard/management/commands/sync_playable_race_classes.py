from django.core.management.base import BaseCommand

from blizzard.sync_race_classes import sync_all_playable_race_classes_from_api


class Command(BaseCommand):
    help = "Sincroniza classes jogáveis de todas as raças."

    def handle(self, *args, **options):
        stats = sync_all_playable_race_classes_from_api()
        self.stdout.write(
            self.style.SUCCESS(
                f"Raças processadas: {stats['races']}, classes gravadas: {stats['classes']}"
            )
        )
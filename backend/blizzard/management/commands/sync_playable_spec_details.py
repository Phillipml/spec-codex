from django.core.management.base import BaseCommand

from blizzard.sync_spec_details import sync_all_playable_spec_details_from_api


class Command(BaseCommand):
    help = "Sincroniza detalhes das specs (description, role, skills PvP com ícones)."

    def add_arguments(self, parser):
        parser.add_argument("--namespace", default="static-us")
        parser.add_argument("--locale", default="pt_BR")
        parser.add_argument("--spec-media-locale", default="en_US")
        parser.add_argument("--spell-media-locale", default="en_US")

    def handle(self, *args, **options):
        stats = sync_all_playable_spec_details_from_api(
            namespace=options["namespace"],
            locale=options["locale"],
            spec_media_locale=options["spec_media_locale"],
            spell_media_locale=options["spell_media_locale"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Specs: {stats['specializations']}, skills: {stats['skills']}"
            )
        )

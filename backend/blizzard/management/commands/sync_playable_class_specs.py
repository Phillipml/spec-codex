from django.core.management.base import BaseCommand

from blizzard.sync_class_specs import sync_all_playable_class_specs_from_api


class Command(BaseCommand):
    help = "Sincroniza classes jogáveis e suas especializações (ícones inclusos)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--namespace",
            default="static-us",
            help="Namespace da Game Data (ex.: static-us).",
        )
        parser.add_argument(
            "--locale",
            default="pt_BR",
            help="Locale para nomes de classe/spec (ex.: pt_BR).",
        )
        parser.add_argument(
            "--spec-media-locale",
            default="en_US",
            help="Locale para mídia das specs (ex.: en_US).",
        )

    def handle(self, *args, **options):
        stats = sync_all_playable_class_specs_from_api(
            namespace=options["namespace"],
            locale=options["locale"],
            spec_media_locale=options["spec_media_locale"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Classes: {stats['classes']}, specs: {stats['specializations']}"
            )
        )

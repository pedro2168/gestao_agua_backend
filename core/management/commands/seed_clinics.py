from django.core.management.base import BaseCommand

from core.management.factories.clinics_generator import ClinicsGenerator
from core.models import Clinics, Point


class Command(BaseCommand):
    help = "Gera clínicas e pontos fake (sem análises)"

    # -------------------------------------------------

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Apaga clínicas e pontos antes de gerar"
        )

    # -------------------------------------------------

    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        generator = ClinicsGenerator()
        clinics = generator.generate()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✔ {len(clinics)} clínicas criadas com sucesso!"
            )
        )

    # -------------------------------------------------

    def _reset(self):
        self.stdout.write("Limpando banco...")

        Point.objects.all().delete()
        Clinics.objects.all().delete()

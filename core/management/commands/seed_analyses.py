from django.core.management.base import BaseCommand
from core.management.factories.analyses_generator import AnalysesGenerator


class Command(BaseCommand):
    help = "Gera análises de água para todos os pontos e parâmetros"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Apaga análises existentes antes de gerar"
        )

    # -------------------------------------------------

    def handle(self, *args, **options):

        generator = AnalysesGenerator()

        created = generator.generate(
            reset=options["reset"]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✔ {created} análises criadas com sucesso!"
            )
        )

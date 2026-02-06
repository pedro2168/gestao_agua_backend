from django.core.management.base import BaseCommand
from core.management.factories.parameters_generator import ParametersGenerator


class Command(BaseCommand):
    help = "Popula tabela WaterParameter (lookup table)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Apaga todos antes de recriar"
        )

    # -------------------------------------------------

    def handle(self, *args, **options):

        generator = ParametersGenerator()

        created, updated = generator.generate(
            reset=options["reset"]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✔ Seed finalizado | criados={created} | atualizados={updated}"
            )
        )

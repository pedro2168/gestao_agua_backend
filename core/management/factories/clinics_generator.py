import random
import string
from django.db import transaction

from core.models import Clinics, Point, PointType


class ClinicsGenerator:
    """
    Gera clínicas e pontos respeitando regras de negócio reais.
    NÃO gera análises (apenas estrutura física).
    """

    # -------------------------
    # CONFIGURAÇÕES
    # -------------------------

    TOTAL_CLINICS_RANGE = (8, 12)

    LARGE_PERCENT = (0.10, 0.25)
    MEDIUM_PERCENT = (0.25, 0.75)

    PORTE_RULES = [{
        "grande": (50, 100),
        "medio": (30, 50),
        "pequeno": (10, 30),
        },
        {
        "grande": (5, 7),
        "medio": (4, 6),
        "pequeno": (3, 4),
        }
    ]

    # -------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------

    @transaction.atomic
    def generate(self):
        total = random.randint(*self.TOTAL_CLINICS_RANGE)

        distribution = self._calculate_distribution(total)

        clinics = []

        index = 0

        for porte, qtd in distribution.items():
            for _ in range(qtd):
                letter = string.ascii_uppercase[index]
                index += 1

                clinic = self._create_clinic(letter, porte)
                clinics.append(clinic)

        return clinics

    # -------------------------------------------------
    # DISTRIBUIÇÃO DE PORTES
    # -------------------------------------------------

    def _calculate_distribution(self, total):
        large = int(total * random.uniform(*self.LARGE_PERCENT))
        medium = int(total * random.uniform(*self.MEDIUM_PERCENT))

        # garante limites
        large = max(1, large)
        medium = max(1, medium)

        if large + medium >= total:
            medium = total - large - 1

        small = total - large - medium

        return {
            "grande": large,
            "medio": medium,
            "pequeno": small,
        }

    # -------------------------------------------------
    # CRIAÇÃO DE CLÍNICA
    # -------------------------------------------------

    def _create_clinic(self, letter, porte):
        min_machines, max_machines = self.PORTE_RULES[0][porte]
        min_infra, max_infra = self.PORTE_RULES[1][porte]

        numero_maximo_maquinas = random.randint(min_machines, max_machines)
        numero_pontos_infraestrutura = random.randint(min_infra, max_infra)

        # 50% a 100% das máquinas permitidas
        maquinas_reais = random.randint(
            int(numero_maximo_maquinas * 0.5),
            numero_maximo_maquinas
        )

        total_points = numero_pontos_infraestrutura + maquinas_reais

        clinic = Clinics.objects.create(
            nome=f"Clinica {letter}",
            numero_maximo_maquinas=numero_maximo_maquinas,
            numero_pontos_infraestrutura=numero_pontos_infraestrutura,
        )

        self._create_points(
            clinic=clinic,
            letter=letter,
            maquinas=maquinas_reais,
            infra=numero_pontos_infraestrutura
        )

        return clinic

    # -------------------------------------------------
    # CRIAÇÃO DE PONTOS
    # -------------------------------------------------

    def _create_points(self, clinic, letter, maquinas, infra):

        points = []

        counter = 1

        # INFRA primeiro
        for _ in range(infra):
            points.append(
                Point(
                    clinica=clinic,
                    tipo=PointType.INFRA,
                    nome=f"Infra {counter}{letter}",
                )
            )
            counter += 1
        
        counter = 1
        # MAQUINAS
        for _ in range(maquinas):
            points.append(
                Point(
                    clinica=clinic,
                    tipo=PointType.MAQUINA,
                    nome=f"Maquina {counter}{letter}",
                )
            )
            counter += 1

        Point.objects.bulk_create(points)

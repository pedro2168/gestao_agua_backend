from django.db import transaction

from core.models import (
    WaterParameter,
    ParameterType,
    Unit,
    Periodicity,
)


class ParametersGenerator:
    """
    Seed determinístico da lookup table WaterParameter.
    Seguro rodar quantas vezes quiser (não duplica).
    """

    PARAMETERS = [
        # nome, categoria, unidade, periodicidade, min, max, obs

        # ---------------- Físico-químicos ----------------
        (
            "pH",
            ParameterType.PH,
            Unit.PERCENTUAL,
            Periodicity.MENSAL,
            6.5,
            8.5,
            "Faixa ideal de pH da água tratada",
        ),
        (
            "Condutividade",
            ParameterType.CONDUTIVIDADE,
            Unit.US_CM,
            Periodicity.MENSAL,
            0,
            1.5,
            "Indicador de sais dissolvidos",
        ),
        (
            "Cloro Livre",
            ParameterType.FISICO_QUIMICO,
            Unit.MG_L,
            Periodicity.SEMESTRAL,
            0,
            0.1,
            "Residual de desinfecção",
        ),

        # ---------------- Microbiológicos ----------------
        (
            "Bactérias Heterotróficas",
            ParameterType.MICROBIOLOGICO,
            Unit.UFC_ML,
            Periodicity.SEMESTRAL,
            0,
            100,
            "Contagem padrão microbiológica",
        ),
        (
            "Coliformes Totais",
            ParameterType.MICROBIOLOGICO,
            Unit.UFC_ML,
            Periodicity.SEMESTRAL,
            0,
            0,
            "Não deve haver presença",
        ),

        # ---------------- Endotoxina ----------------
        (
            "Endotoxina",
            ParameterType.ENDOTOXINA,
            Unit.EU_ML,
            Periodicity.ANUAL,
            0,
            0.25,
            "Limite crítico para hemodiálise",
        ),
    ]

    # -------------------------------------------------

    @transaction.atomic
    def generate(self, reset=False):

        if reset:
            WaterParameter.objects.all().delete()

        created = 0
        updated = 0

        for (
            nome,
            categoria,
            unidade,
            periodicidade,
            min_v,
            max_v,
            obs,
        ) in self.PARAMETERS:

            obj, was_created = WaterParameter.objects.update_or_create(
                nome=nome,  # unique=True → chave natural perfeita
                defaults={
                    "categoria": categoria,
                    "unidade": unidade,
                    "periodicidade": periodicidade,
                    "limite_minimo": min_v,
                    "limite_maximo": max_v,
                    "observacoes": obs,
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        return created, updated

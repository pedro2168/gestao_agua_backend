import random
from datetime import timedelta
from django.utils import timezone
from django.db import transaction

from core.models import (
    Point,
    WaterParameter,
    WaterAnalysis,
    AnalysisResult,
    Periodicity,
)


class AnalysesGenerator:
    """
    Gera análises de água respeitando:
    - 1–5% reprovadas (globais)
    - 10–20% atrasadas
    - 1 análise por (ponto × parâmetro)
    """

    REPROVADO_RANGE = (0.01, 0.05)
    ATRASO_RANGE = (0.10, 0.20)

    # -------------------------------------------------

    @transaction.atomic
    def generate(self, reset=False):

        if reset:
            WaterAnalysis.objects.all().delete()

        pontos = list(Point.objects.all())
        parametros = list(WaterParameter.objects.all())

        total = len(pontos) * len(parametros)

        if total == 0:
            return 0

        # -----------------------------
        # define quantidades globais
        # -----------------------------

        n_reprovadas = int(total * random.uniform(*self.REPROVADO_RANGE))
        n_atrasadas = int(total * random.uniform(*self.ATRASO_RANGE))

        reprovadas_idx = set(random.sample(range(total), n_reprovadas))
        atrasadas_idx = set(random.sample(range(total), n_atrasadas))

        hoje = timezone.now().date()

        counter = 0
        created = 0

        # -----------------------------
        # geração
        # -----------------------------

        for ponto in pontos:
            for parametro in parametros:

                is_reprovado = counter in reprovadas_idx
                is_atrasado = counter in atrasadas_idx
                counter += 1

                valor, resultado = self._gerar_valor(parametro, is_reprovado)

                data_coleta = self._gerar_data(
                    parametro,
                    hoje,
                    is_atrasado
                )

                WaterAnalysis.objects.create(
                    ponto=ponto,
                    parametro=parametro,
                    valor=valor,
                    resultado=resultado,
                    data_da_coleta=data_coleta,
                )

                created += 1

        return created

    # -------------------------------------------------
    # VALORES
    # -------------------------------------------------

    def _gerar_valor(self, parametro, reprovado):

        min_v = parametro.limite_minimo or 0
        max_v = parametro.limite_maximo or 10
        span = max_v - min_v

        if reprovado:
            # força fora do range
            if random.random() < 0.5:
                valor = min_v - span * random.uniform(0.2, 0.8)
            else:
                valor = max_v + span * random.uniform(0.2, 0.8)

            return round(valor, 3), AnalysisResult.REJEITADO

        # aprovado
        valor = random.uniform(min_v, max_v)
        return round(valor, 3), AnalysisResult.APROVADO

    # -------------------------------------------------
    # DATAS
    # -------------------------------------------------

    def _gerar_data(self, parametro, hoje, atrasado):

        dias_periodo = {
            Periodicity.MENSAL: 30,
            Periodicity.SEMESTRAL: 182,
            Periodicity.ANUAL: 365,
        }[parametro.periodicidade]

        if not atrasado:
            # dentro do prazo normal
            return hoje - timedelta(days=random.randint(0, dias_periodo))

        # -----------------------------
        # atrasado (respeitando limites)
        # -----------------------------

        if parametro.periodicidade == Periodicity.ANUAL:
            atraso_extra = random.randint(1, 365)

        elif parametro.periodicidade == Periodicity.SEMESTRAL:
            atraso_extra = random.randint(1, 182)

        else:  # mensal
            atraso_extra = random.randint(1, 90)

        return hoje - timedelta(days=dias_periodo + atraso_extra)

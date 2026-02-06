import math
from pathlib import Path
from collections import defaultdict
from datetime import date
from django.utils import timezone
from ortools.sat.python import cp_model
from dateutil.relativedelta import relativedelta

from core.models import (
    WaterAnalysis,
    Periodicity,
    AnalysisResult,
)


# =====================================================
# PESOS
# =====================================================

W_ATRASO_DIA = 5
W_REPROVADA_DIA = 10
W_DESVIO_MES = 20
W_DESBALANCEAMENTO = 3
FOLGA_MENSAL = 1.1


# =====================================================

def run_scheduler():

    now = timezone.localtime()
    hoje = now.date()

    # 👉 referência segura para simulação
    first_day_this_month = date(hoje.year, hoje.month, 1)

    analyses = list(
        WaterAnalysis.objects
        .select_related("ponto__clinica", "parametro")
        .filter(parametro__periodicidade__in=[
            Periodicity.ANUAL,
            Periodicity.SEMESTRAL,
        ])
    )

    N = len(analyses)

    # =================================================
    # BASELINE
    # =================================================

    baseline_atrasadas = sum(
        1 for a in analyses
        if a.data_da_proxima_coleta < hoje
    )

    baseline_reprovadas = sum(
        1 for a in analyses
        if a.resultado == AnalysisResult.REJEITADO
    )

    if N == 0:
        print("Sem análises elegíveis.")
        return {}

    # -------------------------------------------------
    # meses = deslocamento 0..11 (mais simples e seguro)
    # -------------------------------------------------

    months = list(range(12))

    max_por_mes = math.ceil(FOLGA_MENSAL * N / 12)

    model = cp_model.CpModel()

    x = {}

    for i in range(N):
        for m in months:
            x[i, m] = model.NewBoolVar(f"x_{i}_{m}")

    # cada análise em exatamente 1 mês
    for i in range(N):
        model.Add(sum(x[i, m] for m in months) == 1)

    # limite mensal
    for m in months:
        model.Add(sum(x[i, m] for i in range(N)) <= max_por_mes)

    # -------------------------------------------------
    # OBJETIVO
    # -------------------------------------------------

    objective_terms = []

    for i, analysis in enumerate(analyses):

        atraso_dias = max(
            (hoje - analysis.data_da_proxima_coleta).days,
            0
        )

        reprovada = analysis.resultado == AnalysisResult.REJEITADO

        ideal_month = analysis.data_da_proxima_coleta.month - 1

        for m in months:

            # mês real via simulação segura
            sim_date = first_day_this_month + relativedelta(months=m)
            month_real = sim_date.month - 1

            cost = atraso_dias * W_ATRASO_DIA

            if reprovada:
                cost += atraso_dias * W_REPROVADA_DIA

            desvio = abs(month_real - ideal_month)
            cost += desvio * W_DESVIO_MES

            objective_terms.append(cost * x[i, m])

    # soft capacity (excesso)
    for m in months:

        load = sum(x[i, m] for i in range(N))

        excesso = model.NewIntVar(0, N, f"excesso_{m}")

        model.Add(excesso >= load - max_por_mes)
        model.Add(excesso >= 0)

        objective_terms.append(W_DESBALANCEAMENTO * excesso)

    model.Minimize(sum(objective_terms))

    # -------------------------------------------------
    # solver
    # -------------------------------------------------

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("Sem solução viável")
        return {}

    result = {}

    # =================================================
    # COLETAR RESULTADOS
    # =================================================

    month_counts = defaultdict(int)
    month_clinic = defaultdict(lambda: defaultdict(int))
    clinic_total = defaultdict(int)
    clinic_atraso = defaultdict(int)
    clinic_reprov = defaultdict(int)

    simulated_atraso_total = 0
    clinic_simulated_atraso = defaultdict(int)

    total_atraso = 0
    total_reprov = 0

    cost_values = []

    for i, analysis in enumerate(analyses):

        chosen_m = next(m for m in months if solver.Value(x[i, m]))

        result[str(analysis.id)] = chosen_m

        clinic = analysis.ponto.clinica.nome

        month_counts[chosen_m] += 1
        month_clinic[chosen_m][clinic] += 1
        clinic_total[clinic] += 1

        atraso = analysis.data_da_proxima_coleta < hoje
        repro = analysis.resultado == AnalysisResult.REJEITADO

        if atraso:
            clinic_atraso[clinic] += 1
            total_atraso += 1

        if repro:
            clinic_reprov[clinic] += 1
            total_reprov += 1

        # --------------------------------------------
        # custo individual
        # --------------------------------------------

        atraso_dias = max((hoje - analysis.data_da_proxima_coleta).days, 0)

        sim_date = first_day_this_month + relativedelta(months=chosen_m)
        month_real = sim_date.month - 1
        ideal_month = analysis.data_da_proxima_coleta.month - 1

        desvio = abs(month_real - ideal_month)

        custo = (
            atraso_dias * W_ATRASO_DIA
            + (atraso_dias * W_REPROVADA_DIA if repro else 0)
            + desvio * W_DESVIO_MES
        )

        cost_values.append(custo)

        # --------------------------------------------
        # simulação atraso pós-plano
        # --------------------------------------------

        sim_delay = max((sim_date - analysis.data_da_proxima_coleta).days, 0)

        if sim_delay > 0:
            simulated_atraso_total += 1
            clinic_simulated_atraso[clinic] += 1

    min_cost = min(cost_values) if cost_values else 0
    max_cost = max(cost_values) if cost_values else 0
    total_cost = sum(cost_values)

    # =================================================
    # RELATÓRIO
    # =================================================

    reports_dir = Path(__file__).parent / "schedule"
    reports_dir.mkdir(exist_ok=True)

    filename = f"generated_schedule_{now.strftime('%d-%m-%Y_%H-%M')}.txt"
    filepath = reports_dir / filename

    lines = []

    lines.append("=" * 80)
    lines.append("PLANO ANUAL DE COLETAS (MILP)")
    lines.append("=" * 80)
    lines.append("")

    lines.append(f"Total análises: {N}")
    lines.append(f"Atrasadas antes: {baseline_atrasadas}")
    lines.append(f"Reprovadas antes: {baseline_reprovadas}")
    lines.append(f"Atrasadas após simulação: {simulated_atraso_total}")
    lines.append("")

    lines.append(f"Custo total: {total_cost}")
    lines.append(f"Custo mínimo: {min_cost}")
    lines.append(f"Custo máximo: {max_cost}")
    lines.append("")

    lines.append("===== RESUMO POR CLÍNICA =====")

    for clinic in sorted(clinic_total):
        lines.append(
            f"{clinic}: "
            f"Total={clinic_total[clinic]} | "
            f"Atrasadas após plano={clinic_simulated_atraso[clinic]}"
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nRelatório salvo em:\n{filepath}\n")

    return result

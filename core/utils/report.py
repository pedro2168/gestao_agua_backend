from pathlib import Path
from django.utils import timezone

from core.models import (
    Clinics,
    Point,
    WaterAnalysis,
    PointType,
    AnalysisResult,
)


# -------------------------------------------------
# helpers
# -------------------------------------------------

def pct(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def generate_report():
    now = timezone.localtime()
    hoje = now.date()

    base_dir = Path(__file__).resolve().parent
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    filename = f"report_{now.strftime('%d-%m-%Y_%H-%M')}.txt"
    filepath = reports_dir / filename

    lines = []

    # =================================================
    # ===== ESTATÍSTICAS GERAIS ========================
    # =================================================

    total_clinics = Clinics.objects.count()

    total_points = Point.objects.count()
    total_infra = Point.objects.filter(tipo=PointType.INFRA).count()
    total_maquinas = Point.objects.filter(tipo=PointType.MAQUINA).count()

    total_analyses = WaterAnalysis.objects.count()

    total_reprovadas = WaterAnalysis.objects.filter(
        resultado=AnalysisResult.REJEITADO
    ).count()

    total_atrasadas = WaterAnalysis.objects.filter(
        data_da_proxima_coleta__lt=hoje
    ).count()

    lines.append("=" * 90)
    lines.append("RELATÓRIO DE QUALIDADE DAS ANÁLISES DE ÁGUA")
    lines.append(f"Gerado em: {now.strftime('%d/%m/%Y %H:%M')}")
    lines.append("=" * 90)
    lines.append("")

    lines.append("===== ESTATÍSTICAS GERAIS =====")
    lines.append(f"Clínicas totais: {total_clinics}")
    lines.append("")

    lines.append("Pontos:")
    lines.append(f"  • Total: {total_points}")
    lines.append(f"  • Infraestrutura: {total_infra}")
    lines.append(f"  • Máquinas: {total_maquinas}")
    lines.append("")

    lines.append(f"Análises totais: {total_analyses}")
    lines.append(
        f"  • Atrasadas: {total_atrasadas} ({pct(total_atrasadas, total_analyses)}%)"
    )
    lines.append(
        f"  • Reprovadas: {total_reprovadas} ({pct(total_reprovadas, total_analyses)}%)"
    )

    lines.append("\n" + "=" * 90 + "\n")

    # =================================================
    # ===== POR CLÍNICA ===============================
    # =================================================

    for clinic in Clinics.objects.all().order_by("nome"):

        pontos = clinic.pontos.all()

        total_pontos = pontos.count()
        infra = pontos.filter(tipo=PointType.INFRA).count()
        maquinas = pontos.filter(tipo=PointType.MAQUINA).count()

        analyses = WaterAnalysis.objects.filter(ponto__clinica=clinic)

        total_analises = analyses.count()

        reprovadas = analyses.filter(
            resultado=AnalysisResult.REJEITADO
        ).count()

        atrasadas = analyses.filter(
            data_da_proxima_coleta__lt=hoje
        ).count()

        # -------------------------------------------------

        lines.append(f"CLÍNICA: {clinic.nome} ({clinic.id})")
        lines.append("-" * 90)

        lines.append("Pontos:")
        lines.append(f"  • Total: {total_pontos}")
        lines.append(f"  • Infraestrutura: {infra}")
        lines.append(f"  • Máquinas: {maquinas} de {clinic.numero_maximo_maquinas} ({pct(maquinas, clinic.numero_maximo_maquinas)})")
        lines.append("")

        lines.append(f"Análises totais: {total_analises}")
        lines.append(
            f"  • Atrasadas: {atrasadas} ({pct(atrasadas, total_analises)}%)"
        )
        lines.append(
            f"  • Reprovadas: {reprovadas} ({pct(reprovadas, total_analises)}%)"
        )

        lines.append("")

        # -------------------------------------------------
        # Pontos problemáticos
        # -------------------------------------------------

        problematic_points = []

        for point in pontos:

            pa = point.analises_agua.all()

            has_reprovado = pa.filter(
                resultado=AnalysisResult.REJEITADO
            ).exists()

            has_atraso = pa.filter(
                data_da_proxima_coleta__lt=hoje
            ).exists()

            if has_reprovado or has_atraso:

                if has_reprovado and has_atraso:
                    status = "Reprovado e Atrasado"
                elif has_reprovado:
                    status = "Reprovado"
                else:
                    status = "Atrasado"

                problematic_points.append(
                    f"- {point.nome} ({point.id}) → {status}"
                )

        if problematic_points:
            lines.append("Pontos com problemas:")
            lines.extend(problematic_points)
        else:
            lines.append("Nenhum ponto com problemas 🎉")

        lines.append("\n")

    # =================================================
    # salvar
    # =================================================

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nRelatório salvo em:\n{filepath}\n")

    return filepath

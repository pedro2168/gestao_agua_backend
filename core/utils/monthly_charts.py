import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path
from django.utils import timezone

from core.models import WaterAnalysis


def generate_monthly_chart():
    """
    Gera gráfico de barras com número de coletas por mês.
    Salva PNG em core/utils/reports/
    """

    hoje = timezone.localtime()

    analyses = WaterAnalysis.objects.all()

    months = []

    for a in analyses:
        if a.data_da_proxima_coleta:
            months.append(a.data_da_proxima_coleta.month)

    counts = Counter(months)

    x = list(range(1, 13))
    y = [counts.get(m, 0) for m in x]

    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    filename = f"monthly_distribution_{hoje.strftime('%d-%m-%Y_%H-%M')}.png"
    filepath = reports_dir / filename

    plt.figure(figsize=(10, 5))
    plt.bar(x, y)
    plt.xlabel("Mês")
    plt.ylabel("Número de coletas")
    plt.title("Distribuição mensal de coletas agendadas")
    plt.xticks(x)

    plt.savefig(filepath, bbox_inches="tight")
    plt.close()

    print(f"\nGráfico salvo em:\n{filepath}\n")

    return filepath

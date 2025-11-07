from core.models import WaterAnalysis, WaterParameter
from typing import List, Optional


def listar_analises(ids: Optional[List[str]] = None):
    if ids:
        return list(WaterAnalysis.objects.filter(id__in=ids))
    return WaterAnalysis.objects.all()

def criar_analise(data):
    parametro = WaterParameter.objects.get(id=data["parametro"])
    analise = WaterAnalysis.objects.create(**data)
    analise.save()  # data_da_proxima_coleta será gerada automaticamente
    return analise

def atualizar_analise(analise_id, data):
    analise = WaterAnalysis.objects.get(id=analise_id)
    for key, value in data.items():
        setattr(analise, key, value)
    analise.save()
    return analise

def deletar_analise(analise_id):
    analise = WaterAnalysis.objects.get(id=analise_id)
    analise.delete()
    return {"message": f"Análise {analise_id} deletada com sucesso."}

from core.models import WaterParameter
from typing import List, Optional

def listar_parametros(ids: Optional[List[str]] = None):
    if ids:
        return WaterParameter.objects.filter(id__in=ids)
    return WaterParameter.objects.all()

def criar_parametro(data):
    return WaterParameter.objects.create(**data)

def atualizar_parametro(parametro_id, data):
    parametro = WaterParameter.objects.get(id=parametro_id)
    for key, value in data.items():
        setattr(parametro, key, value)
    parametro.save()
    return parametro

def deletar_parametro(parametro_id):
    parametro = WaterParameter.objects.get(id=parametro_id)
    parametro.delete()
    return {"message": f"Parâmetro {parametro_id} deletado com sucesso."}

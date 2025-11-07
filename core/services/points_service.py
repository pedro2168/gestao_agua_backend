from core.models import Point, Clinics
from core.schemas import PointSchema
from typing import List, Optional
from django.core.exceptions import ValidationError

def listar_pontos(ids: Optional[List[str]] = None):
    if ids:
        pontos = Point.objects.filter(id__in=ids)
        return [PointSchema.model_validate(p) for p in pontos]
    return Point.objects.all()

def criar_ponto(data):
    tipo = data.get("tipo")
    clinica_id = data.get("clinica")

    if tipo == "INFRA" and not clinica_id:
        raise ValidationError("Pontos de infraestrutura precisam estar vinculados a uma clínica.")

    if clinica_id:
        try:
            data["clinica"] = Clinics.objects.get(id=clinica_id)
        except Clinics.DoesNotExist:
            raise ValidationError(f"Clínica com id {clinica_id} não encontrada.")

    ponto = Point.objects.create(**data)
    return PointSchema.model_validate(ponto)

def atualizar_ponto(point_id, data):
    ponto = Point.objects.get(id=point_id)
    for key, value in data.items():
        setattr(ponto, key, value)
    ponto.save()
    return ponto

def deletar_ponto(point_id):
    ponto = Point.objects.get(id=point_id)
    ponto.delete()
    return {"message": f"Ponto {point_id} deletado com sucesso."}

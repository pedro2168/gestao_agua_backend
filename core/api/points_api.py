from ninja import Router, Query
from typing import Optional, List
from core.schemas import PointSchema, PointSchemaUpdate, PointSchemaCreate
from core.services import points_service

router = Router(tags=["Pontos de Água"])

@router.get("/", response=list[PointSchema])
def listar_pontos(request, ids: Optional[List[str]] = Query(None)):
    return points_service.listar_pontos(ids)

@router.post("/", response=PointSchema)
def criar_ponto(request, payload: PointSchemaCreate):
    return points_service.criar_ponto(payload.model_dump(exclude_unset=True))

@router.put("/{point_id}", response=PointSchema)
def atualizar_ponto(request, point_id: str, payload: PointSchemaUpdate):
    return points_service.atualizar_ponto(point_id, payload.model_dump(exclude_unset=True))

@router.delete("/{point_id}")
def deletar_ponto(request, point_id: str):
    return points_service.deletar_ponto(point_id)

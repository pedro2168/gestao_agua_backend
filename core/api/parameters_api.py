from ninja import Router, Query
from typing import Optional, List
from core.schemas import WaterParameterSchema, WaterParameterSchemaUpdate
from core.services import parameters_service

router = Router(tags=["Parâmetros de Análise"])

@router.get("/", response=list[WaterParameterSchema])
def listar_parametros(request, ids: Optional[List[str]] = Query(None)):
    return parameters_service.listar_parametros(ids)

@router.post("/", response=WaterParameterSchema)
def criar_parametro(request, payload: WaterParameterSchema):
    return parameters_service.criar_parametro(payload.dict(exclude_unset=True))

@router.put("/{parametro_id}", response=WaterParameterSchema)
def atualizar_parametro(request, parametro_id: str, payload: WaterParameterSchemaUpdate):
    return parameters_service.atualizar_parametro(parametro_id, payload.dict(exclude_unset=True))

@router.delete("/{parametro_id}")
def deletar_parametro(request, parametro_id: str):
    return parameters_service.deletar_parametro(parametro_id)

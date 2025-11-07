from ninja import Router, Query
from typing import Optional, List
from core.schemas import WaterAnalysisSchema, WaterAnalysisSchemaUpdate
from core.services import analysis_service

router = Router(tags=["Análises de Água"])

@router.get("/", response=list[WaterAnalysisSchema])
def listar_analises(request, ids: Optional[List[str]] = Query(None)):
    return analysis_service.listar_analises(ids)

@router.post("/", response=WaterAnalysisSchema)
def criar_analise(request, payload: WaterAnalysisSchema):
    return analysis_service.criar_analise(payload.dict(exclude_unset=True))

@router.put("/{analise_id}", response=WaterAnalysisSchema)
def atualizar_analise(request, analise_id: str, payload: WaterAnalysisSchemaUpdate):
    return analysis_service.atualizar_analise(analise_id, payload.dict(exclude_unset=True))

@router.delete("/{analise_id}")
def deletar_analise(request, analise_id: str):
    return analysis_service.deletar_analise(analise_id)

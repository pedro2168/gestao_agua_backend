from typing import Optional, List
from ninja import Query, Router, Form
from core.schemas import ClinicSchema, ClinicSchemaUpdate, PointSchema
from core.services import clinics_service

router = Router(tags=["Clínicas"])

@router.get("/", response=list[ClinicSchema])
def get_clinics(request, ids: List[str] = Query(None)):
    return clinics_service.listar_clinicas(ids)

@router.post("/", response=ClinicSchema)
def post_clinic(request, payload: ClinicSchema):
    return clinics_service.criar_clinica(payload)

@router.put("/{clinic_id}", response=ClinicSchema)
def put_clinic(request, clinic_id: str, payload: ClinicSchemaUpdate):
    clinic = clinics_service.atualizar_clinica(clinic_id, payload)
    if clinic is None:
        return router.create_response(request, {"detail": "Clinic not found"}, status=404)
    return clinic

@router.delete("/{clinic_id}")
def delete_clinic(request, clinic_id: str):
    deleted = clinics_service.deletar_clinica(clinic_id)
    if not deleted:
        return router.create_response(request, {"detail": "Clinic not found"}, status=404)
    return {"success": True}

@router.get("/points/{clinic_id}", response=list[PointSchema])
def get_clinic_points(request, clinic_id: str):
    return clinics_service.listar_pontos_clinica(clinic_id)
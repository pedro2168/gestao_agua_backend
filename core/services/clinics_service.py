import re
from typing import List, Optional
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models import Clinics, Point
from core.schemas import ClinicSchema, ClinicSchemaUpdate, PointSchema

def validar_cnpj(cnpj: str):
    padrao = r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$'
    if not re.match(padrao, cnpj):
        raise ValidationError("CNPJ inválido. Use o formato 00.000.000/0000-00.")


def validar_email(email: str):
    from email_validator import validate_email, EmailNotValidError
    try:
        validate_email(email)
    except EmailNotValidError:
        raise ValidationError("E-mail inválido.")


def validar_telefone(telefone: str):
    padrao = r'^\(?\d{2}\)?\s?\d{4,5}-\d{4}$'  # exemplo: (11) 98888-7777
    if not re.match(padrao, telefone):
        raise ValidationError("Telefone inválido. Use o formato (XX) XXXXX-XXXX.")


def listar_clinicas(ids: Optional[List[str]] = None):
    if ids:
        return list(Clinics.objects.filter(id__in=ids))
    return list(Clinics.objects.all())


def criar_clinica(data: ClinicSchema):
    validar_cnpj(data.cnpj)
    validar_email(data.email)
    validar_telefone(data.telefone)

    if Clinics.objects.filter(cnpj=data.cnpj).exists():
        raise ValidationError("Já existe uma clínica com esse CNPJ.")

    try:
        clinic = Clinics.objects.create(**data.model_dump(exclude_unset=True))
        return clinic
    except IntegrityError as e:
        raise ValidationError(f"Erro ao criar clínica: {str(e)}")


def atualizar_clinica(clinic_id: str, data: ClinicSchemaUpdate):
    try:
        clinic = Clinics.objects.get(id=clinic_id)
    except Clinics.DoesNotExist:
        return None

    updates = data.model_dump(exclude_unset=True)

    if "cnpj" in updates:
        validar_cnpj(updates["cnpj"])
    if "email" in updates:
        validar_email(updates["email"])
    if "telefone" in updates:
        validar_telefone(updates["telefone"])

    for attr, value in updates.items():
        setattr(clinic, attr, value)

    clinic.save()
    return clinic


def deletar_clinica(clinic_id: str) -> bool:
    """Deleta uma clínica existente."""
    deleted, _ = Clinics.objects.filter(id=clinic_id).delete()
    return deleted > 0

def listar_pontos_clinica(clinic_id: str):
    return Point.objects.filter(clinica=clinic_id)

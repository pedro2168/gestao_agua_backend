from pydantic import BaseModel, Field, EmailStr, ConfigDict, StringConstraints, field_serializer
from typing import Annotated, Optional
from uuid import UUID
from datetime import date
from enum import Enum

# ========= ENUMS =========

class PointType(str, Enum):
    INFRA = "INFRA"
    MAQUINA = "MAQUINA"


class ParameterType(str, Enum):
    FISICO_QUIMICO = "FISICO-QUIMICO"
    MICROBIOLOGICO = "MICROBIOLOGICO"


class Unit(str, Enum):
    UG_ML = "μg/ml"
    NG_ML = "ng/ml"
    MG_L = "mg/L"
    PERCENTUAL = "%"


class Periodicity(str, Enum):
    MENSAL = "MENSAL"
    SEMESTRAL = "SEMESTRAL"
    ANUAL = "ANUAL"


class AnalysisResult(str, Enum):
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"

# ========= CLINICS =========

class ClinicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = None
    nome: str
    cnpj: Optional[Annotated[str, StringConstraints(pattern=r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")]] = Field(
        ..., description="CNPJ no formato 00.000.000/0000-00"
    )
    endereco: Optional[str] = None
    responsavel_tecnico: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, description="Telefone da clínica")
    numero_maximo_maquinas: int
    numero_pontos_infraestrutura: int = 0

class ClinicSchemaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: Optional[str] = None
    cnpj: Optional[
        Annotated[str, StringConstraints(pattern=r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")]
    ] = None
    endereco: Optional[str] = None
    responsavel_tecnico: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    numero_maximo_maquinas: Optional[int] = None

    # ========= POINT =========

class PointSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    tipo: PointType
    nome: str
    clinica: Optional[ClinicSchema] = None
    analises_de_agua: Optional[dict] = Field(
        default_factory=dict, description="Informações adicionais de análises de água (JSON)"
    )

class PointSchemaCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: PointType
    nome: str
    clinica: Optional[UUID] = Field(
        None, description="ID da clínica associada (obrigatório se tipo=INFRA)"
    )
    analises_de_agua: Optional[dict] = Field(default_factory=dict)

class PointSchemaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: Optional[PointType] = None
    nome: Optional[str] = None
    clinica: Optional[UUID] = None
    analises_de_agua: Optional[dict] = None


# ========= WATER PARAMETER =========

class WaterParameterSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    nome: str
    categoria: ParameterType
    unidade: Unit
    periodicidade: Periodicity = Periodicity.SEMESTRAL
    limite_minimo: Optional[float] = None
    limite_maximo: Optional[float] = None
    observacoes: Optional[str] = None


class WaterParameterSchemaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: Optional[str] = None
    categoria: Optional[ParameterType] = None
    unidade: Optional[Unit] = None
    periodicidade: Optional[Periodicity] = None
    limite_minimo: Optional[float] = None
    limite_maximo: Optional[float] = None
    observacoes: Optional[str] = None


# ========= WATER ANALYSIS =========

class WaterAnalysisSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    ponto: UUID = Field(..., description="ID do ponto onde a análise foi realizada")
    parametro: UUID = Field(..., description="ID do parâmetro analisado")
    valor: float
    resultado: Optional[AnalysisResult] = None
    data_da_coleta: Optional[date] = Field(default_factory=date.today)
    data_da_proxima_coleta: Optional[date] = None


class WaterAnalysisSchemaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ponto: Optional[UUID] = None
    parametro: Optional[UUID] = None
    valor: Optional[float] = None
    resultado: Optional[AnalysisResult] = None
    data_da_coleta: Optional[date] = None
    data_da_proxima_coleta: Optional[date] = None
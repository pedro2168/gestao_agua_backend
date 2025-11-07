import uuid
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

class PointType(models.TextChoices):
    INFRA = "INFRA", "Infraestrutura"
    MAQUINA = "MAQUINA", "Máquina"

class ParameterType(models.TextChoices):
    FISICO_QUIMICO = "FISICO-QUIMICO", "Físico-Químico"
    MICROBIOLOGICO = "MICROBIOLOGICO", "Microbiológico"


class Unit(models.TextChoices):
    UG_ML = "μg/ml", "μg/ml"
    NG_ML = "ng/ml", "ng/ml"
    MG_L = "mg/L", "mg/L"
    PERCENTUAL = "%", "%"


class AnalysisResult(models.TextChoices):
    APROVADO = "APROVADO", "Aprovado"
    REJEITADO = "REJEITADO", "Rejeitado"


class Periodicity(models.TextChoices):
    MENSAL = "MENSAL", "Mensal"
    SEMESTRAL = "SEMESTRAL", "Semestral"
    ANUAL = "ANUAL", "Anual"


class Clinics(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    nome = models.CharField(max_length=150)

    cnpj = models.CharField(
        max_length=18,  # formato 00.000.000/0000-00
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
                message='CNPJ deve estar no formato 00.000.000/0000-00'
            )
        ]
    )

    endereco = models.CharField(max_length=255, blank=True, null=True)
    responsavel_tecnico = models.CharField(max_length=150, blank=True, null=True)

    email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        validators=[EmailValidator(message="Informe um email válido.")]
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{0,3}?[ -]?\(?\d{2,3}\)?[ -]?\d{4,5}[ -]?\d{4}$',
                message='Telefone deve estar em formato válido (ex: +55 11 91234-5678)'
            )
        ]
    )

    numero_maximo_maquinas = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Número máximo de máquinas"
    )

    numero_pontos_infraestrutura = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de pontos de infraestrutura"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Point(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=10, choices=PointType.choices)
    nome = models.CharField(max_length=150)
    clinica = models.ForeignKey(
        Clinics,
        on_delete=models.CASCADE,
        null=True,  # opcional para máquinas
        blank=True,
        related_name="pontos",
    )
    # Placeholder para o futuro campo complexo
    analises_de_agua = models.JSONField(default=dict, blank=True)

    def clean(self):
        # regra de negócio: INFRA precisa ter clínica
        if self.tipo == PointType.INFRA and self.clinica is None:
            raise ValidationError("Pontos de infraestrutura devem estar vinculados a uma clínica.")

    def save(self, *args, **kwargs):
        self.full_clean()  # força a validação
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

class WaterParameter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=20, choices=ParameterType.choices)
    unidade = models.CharField(max_length=10, choices=Unit.choices)
    periodicidade = models.CharField(max_length=15, choices=Periodicity.choices, default=Periodicity.SEMESTRAL)
    limite_minimo = models.FloatField(null=True, blank=True)
    limite_maximo = models.FloatField(null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.categoria})"

class WaterAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ponto = models.ForeignKey(
        Point, on_delete=models.CASCADE, related_name="analises_agua"
    )
    parametro = models.ForeignKey(
        WaterParameter, on_delete=models.CASCADE, related_name="analises"
    )
    valor = models.FloatField()
    resultado = models.CharField(max_length=15, choices=AnalysisResult.choices)
    data_da_coleta = models.DateField(default=timezone.now)
    data_da_proxima_coleta = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Define automaticamente data da próxima coleta com base na periodicidade do parâmetro"""
        if not self.data_da_proxima_coleta and self.parametro:
            if self.parametro.periodicidade == "MENSAL":
                self.data_da_proxima_coleta = self.data_da_coleta + timedelta(days=30)
            elif self.parametro.periodicidade == "SEMESTRAL":
                self.data_da_proxima_coleta = self.data_da_coleta + timedelta(days=182)
            elif self.parametro.periodicidade == "ANUAL":
                self.data_da_proxima_coleta = self.data_da_coleta + timedelta(days=365)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parametro.nome} - {self.ponto.nome} ({self.data_da_coleta})"
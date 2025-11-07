from django.contrib import admin

# Register your models here.

from .models import Clinics

@admin.register(Clinics)
class ClinicsAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "cnpj", "numero_maximo_maquinas", "numero_pontos_infraestrutura")

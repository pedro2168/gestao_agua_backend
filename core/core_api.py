from ninja import NinjaAPI
from pydantic import ValidationError
from django.http import JsonResponse
from core.api.clinics_api import router as clinics_router
from core.api.points_api import router as points_router
from core.api.analysis_api import router as analysis_router
from core.api.parameters_api import router as parameters_router

api = NinjaAPI(title="Gestão Água API")

@api.exception_handler(ValidationError)
def validation_errors(request, exc):
    return JsonResponse({"detail": str(exc)}, status=400)

api.add_router("/clinics", clinics_router)
api.add_router("/points/", points_router)
api.add_router("/parameters/", parameters_router)
api.add_router("/analysis/", analysis_router)
"""
URLs para el servicio de Incidencias
Integrante 4 - Gestión de Incidencias
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from presentacion.views.incidencia_views import IncidenciaViewSet

# Crear router
router = DefaultRouter()
router.register(r"", IncidenciaViewSet, basename="incidencia")

# URLs generadas automáticamente:
# GET    /api/incidencias/              → list
# POST   /api/incidencias/              → create
# GET    /api/incidencias/{id}/         → retrieve
# PATCH  /api/incidencias/{id}/asignar/ → asignar
# PATCH  /api/incidencias/{id}/clasificar/ → clasificar
# PATCH  /api/incidencias/{id}/resolver/ → resolver
# PATCH  /api/incidencias/{id}/cerrar/  → cerrar
# PATCH  /api/incidencias/{id}/observacion/ → observacion
# GET    /api/incidencias/activas/      → activas
# GET    /api/incidencias/resumen/      → resumen
# GET    /api/incidencias/tipos/        → tipos
# GET    /api/incidencias/prioridades/  → prioridades
# GET    /api/incidencias/estados/      → estados

urlpatterns = [
    path("", include(router.urls)),
]
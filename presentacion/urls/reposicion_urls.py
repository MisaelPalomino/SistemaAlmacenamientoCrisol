"""
URLs para el servicio de Reposiciones
Integrante 5 - Gestión de Reposiciones
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from presentacion.views.reposicion_views import ReposicionViewSet

# Crear router
router = DefaultRouter()
router.register(r"", ReposicionViewSet, basename="reposicion")

# URLs generadas automáticamente:
# GET    /api/reposiciones/              → list
# POST   /api/reposiciones/              → create
# GET    /api/reposiciones/{id}/         → retrieve
# PATCH  /api/reposiciones/{id}/aprobar/ → aprobar
# PATCH  /api/reposiciones/{id}/ejecutar/ → ejecutar
# PATCH  /api/reposiciones/{id}/completar/ → completar
# PATCH  /api/reposiciones/{id}/cancelar/ → cancelar
# GET    /api/reposiciones/pendientes/   → pendientes
# GET    /api/reposiciones/resumen/      → resumen

urlpatterns = [
    path("", include(router.urls)),
]

"""
URLs principales del proyecto
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Health Check
    # ===== SERVICIO DE PRODUCTOS =====
    path("api/productos/", include("presentacion.urls.producto_urls")),
    # ===== SERVICIO DE RECEPCIONES =====
    path("api/recepciones/", include("presentacion.urls.recepcion_urls")),
    path("api/reposiciones/", include("presentacion.urls.reposicion_urls")),
    path("api/incidencias/", include("presentacion.urls.incidencia_urls")),
]

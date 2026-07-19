"""
URLs para el servicio de Productos con ViewSet
Integrante 1 - Gestión de Productos
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from presentacion.views.producto_views import ProductoViewSet

# Crear router
router = DefaultRouter()
router.register(r'', ProductoViewSet, basename='producto')

# URLs generadas automáticamente:
# GET    /api/productos/              → list
# POST   /api/productos/              → create
# GET    /api/productos/{id}/         → retrieve
# PUT    /api/productos/{id}/         → update
# DELETE /api/productos/{id}/         → destroy
# GET    /api/productos/buscar/       → buscar
# PATCH  /api/productos/{id}/stock/   → stock
# PATCH  /api/productos/{id}/precios/ → precios
# GET    /api/productos/alertas_stock_bajo/ → alertas_stock_bajo

urlpatterns = [
    path('', include(router.urls)),
]
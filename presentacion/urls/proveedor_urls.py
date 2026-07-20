from django.urls import include, path
from rest_framework.routers import DefaultRouter

from presentacion.views.proveedor_views import ProveedorViewSet


router = DefaultRouter()
router.register(r"", ProveedorViewSet, basename="proveedor")

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from presentacion.views.recepcion_views import RecepcionViewSet

router = DefaultRouter()
router.register(r'', RecepcionViewSet, basename='recepcion')

urlpatterns = [
    path('', include(router.urls)),
]

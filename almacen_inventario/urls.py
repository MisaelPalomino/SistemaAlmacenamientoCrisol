"""
URLs principales del proyecto
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Health Check
def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'Sistema de Almacenamiento - Librerías Crisol',
        'version': '1.0.0',
        'integrante': 'Integrante 1 - Servicio de Productos'
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check
    path('api/health/', health_check, name='health_check'),
    
    # ===== SERVICIO DE PRODUCTOS =====
    # ✅ Incluir las URLs de productos
    path('api/productos/', include('presentacion.urls.producto_urls')),
]
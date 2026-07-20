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
        'integrantes': [
            'Integrante 1 - Servicio de Productos',
            'Integrante 2 - Servicio de Proveedores',
            'Integrante 3 - Servicio de Recepciones',
        ]
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check
    path('api/health/', health_check, name='health_check'),
    
    # ===== SERVICIO DE PRODUCTOS =====
    path('api/productos/', include('presentacion.urls.producto_urls')),
    path('api/proveedores/', include('presentacion.urls.proveedor_urls')),
    path('api/recepciones/', include('presentacion.urls.recepcion_urls')),
]

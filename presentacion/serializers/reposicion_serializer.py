"""
Serializador para Solicitudes de Reposición
Integrante 5 - Gestión de Reposiciones
"""

from rest_framework import serializers
from dominio.models import SolicitudReposicion, Producto


class SolicitudReposicionSerializer(serializers.ModelSerializer):
    """
    Serializador para SolicitudReposicion
    """

    # ========== CAMPOS CALCULADOS ==========
    esta_pendiente = serializers.BooleanField(read_only=True)
    esta_activa = serializers.BooleanField(read_only=True)
    porcentaje_ejecutado = serializers.FloatField(read_only=True)
    es_urgente = serializers.BooleanField(read_only=True)
    necesita_aprobacion = serializers.BooleanField(read_only=True)

    # ========== CAMPOS RELACIONADOS ==========
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    producto_isbn = serializers.CharField(source="producto.isbn", read_only=True)

    class Meta:
        model = SolicitudReposicion
        fields = [
            "id",
            "numero_solicitud",
            "producto",
            "producto_nombre",
            "producto_isbn",
            "cantidad_solicitada",
            "cantidad_aprobada",
            "cantidad_repuesta",
            "fecha_solicitud",
            "fecha_aprobacion",
            "fecha_ejecucion",
            "fecha_completada",
            "estado",
            "prioridad",
            "motivo",
            "aprobado_por",
            "ejecutado_por",
            "observaciones",
            "proveedor",
            # Campos calculados
            "esta_pendiente",
            "esta_activa",
            "porcentaje_ejecutado",
            "es_urgente",
            "necesita_aprobacion",
        ]
        read_only_fields = [
            "id",
            "fecha_solicitud",
            "fecha_aprobacion",
            "fecha_ejecucion",
            "fecha_completada",
        ]

    # ========== VALIDACIONES ==========
    def validate_producto(self, value):
        """Valida que el producto exista y esté activo"""
        try:
            producto = Producto.objects.get(id=value.id, activo=True)
        except Producto.DoesNotExist:
            raise serializers.ValidationError(
                f"Producto con ID {value.id} no encontrado o inactivo"
            )
        return value

    def validate_cantidad_solicitada(self, value):
        """Valida que la cantidad solicitada sea positiva"""
        if value <= 0:
            raise serializers.ValidationError(
                "La cantidad solicitada debe ser positiva"
            )
        return value


class ReposicionListSerializer(serializers.ModelSerializer):
    """
    Serializador simplificado para listar solicitudes
    """

    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    porcentaje_ejecutado = serializers.FloatField(read_only=True)

    class Meta:
        model = SolicitudReposicion
        fields = [
            "id",
            "numero_solicitud",
            "producto_nombre",
            "cantidad_solicitada",
            "cantidad_aprobada",
            "cantidad_repuesta",
            "estado",
            "prioridad",
            "fecha_solicitud",
            "porcentaje_ejecutado",
        ]


class ReposicionEstadoSerializer(serializers.ModelSerializer):
    """
    Serializador para cambios de estado
    """

    class Meta:
        model = SolicitudReposicion
        fields = [
            "id",
            "numero_solicitud",
            "estado",
            "fecha_aprobacion",
            "fecha_ejecucion",
            "fecha_completada",
        ]
        read_only_fields = [
            "id",
            "numero_solicitud",
            "fecha_aprobacion",
            "fecha_ejecucion",
            "fecha_completada",
        ]

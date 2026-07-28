"""
Serializador para Incidencias
Integrante 4 - Gestión de Incidencias
"""

from rest_framework import serializers
from dominio.models import Incidencia, Producto, Recepcion


class IncidenciaSerializer(serializers.ModelSerializer):
    """
    Serializador para Incidencia
    """

    # ========== CAMPOS CALCULADOS ==========
    tiempo_resolucion_horas = serializers.FloatField(read_only=True)
    es_critica = serializers.BooleanField(read_only=True)
    esta_activa = serializers.BooleanField(read_only=True)
    requiere_atencion_inmediata = serializers.BooleanField(read_only=True)

    # ========== CAMPOS RELACIONADOS ==========
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    producto_isbn = serializers.CharField(source="producto.isbn", read_only=True)
    recepcion_numero = serializers.CharField(
        source="recepcion.numero_recepcion", read_only=True
    )

    class Meta:
        model = Incidencia
        fields = [
            "id",
            "codigo_incidencia",
            "producto",
            "producto_nombre",
            "producto_isbn",
            "recepcion",
            "recepcion_numero",
            "tipo",
            "prioridad",
            "estado",
            "descripcion",
            "cantidad_afectada",
            "impacto_economico",
            "fecha_registro",
            "fecha_asignacion",
            "fecha_resolucion",
            "fecha_cierre",
            "responsable",
            "asignado_a",
            "observaciones",
            "solucion_aplicada",
            "accion_correctiva",
            # Campos calculados
            "tiempo_resolucion_horas",
            "es_critica",
            "esta_activa",
            "requiere_atencion_inmediata",
        ]
        read_only_fields = [
            "id",
            "fecha_registro",
            "fecha_asignacion",
            "fecha_resolucion",
            "fecha_cierre",
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

    def validate_recepcion(self, value):
        """Valida que la recepción exista (si se proporciona)"""
        if value:
            try:
                recepcion = Recepcion.objects.get(id=value.id)
            except Recepcion.DoesNotExist:
                raise serializers.ValidationError(
                    f"Recepción con ID {value.id} no encontrada"
                )
        return value

    def validate_cantidad_afectada(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad afectada debe ser positiva")
        return value

    def validate_tipo(self, value):
        tipos = [t[0] for t in Incidencia.TIPOS]
        if value not in tipos:
            raise serializers.ValidationError(
                f"Tipo inválido. Opciones: {', '.join(tipos)}"
            )
        return value

    def validate_prioridad(self, value):
        prioridades = [p[0] for p in Incidencia.PRIORIDADES]
        if value not in prioridades:
            raise serializers.ValidationError(
                f"Prioridad inválida. Opciones: {', '.join(prioridades)}"
            )
        return value


class IncidenciaListSerializer(serializers.ModelSerializer):
    """
    Serializador simplificado para listar incidencias
    """

    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    tiempo_resolucion_horas = serializers.FloatField(read_only=True)

    class Meta:
        model = Incidencia
        fields = [
            "id",
            "codigo_incidencia",
            "producto_nombre",
            "tipo",
            "prioridad",
            "estado",
            "cantidad_afectada",
            "fecha_registro",
            "tiempo_resolucion_horas",
            "asignado_a",
        ]


class IncidenciaEstadoSerializer(serializers.ModelSerializer):
    """
    Serializador para cambios de estado
    """

    class Meta:
        model = Incidencia
        fields = [
            "id",
            "codigo_incidencia",
            "estado",
            "fecha_asignacion",
            "fecha_resolucion",
            "fecha_cierre",
        ]
        read_only_fields = ["id", "codigo_incidencia"]


class IncidenciaTipoSerializer(serializers.Serializer):
    """
    Serializador para listar tipos
    """

    codigo = serializers.CharField()
    descripcion = serializers.CharField()
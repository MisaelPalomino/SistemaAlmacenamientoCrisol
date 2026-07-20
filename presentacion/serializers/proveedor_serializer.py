from rest_framework import serializers
from dominio.models import Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    calificacion = serializers.CharField(max_length=1, required=False)

    class Meta:
        model = Proveedor
        fields = [
            "id",
            "ruc",
            "razon_social",
            "nombre_comercial",
            "direccion_calle",
            "direccion_numero",
            "direccion_distrito",
            "direccion_provincia",
            "direccion_departamento",
            "direccion_codigo_postal",
            "direccion_referencia",
            "email",
            "telefono",
            "telefono_alternativo",
            "especialidad",
            "plazo_entrega_dias",
            "condiciones_pago",
            "calificacion",
            "es_nacional",
            "activo",
            "fecha_registro",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "id",
            "activo",
            "fecha_registro",
            "fecha_actualizacion",
        ]

    def validate_ruc(self, value):
        ruc = str(value).strip()

        if len(ruc) != 11 or not ruc.isdigit():
            raise serializers.ValidationError(
                "El RUC debe contener exactamente 11 dígitos"
            )

        proveedores = Proveedor.objects.filter(ruc=ruc)
        if self.instance is not None:
            proveedores = proveedores.exclude(id=self.instance.id)

        if proveedores.exists():
            raise serializers.ValidationError(
                f"Ya existe un proveedor con el RUC {ruc}"
            )

        return ruc

    def validate_calificacion(self, value):
        calificacion = str(value).strip().upper()
        if calificacion not in {"A", "B", "C", "D"}:
            raise serializers.ValidationError(
                "La calificación debe ser A, B, C o D"
            )
        return calificacion

    def validate_plazo_entrega_dias(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El plazo de entrega debe ser mayor que cero"
            )
        return value

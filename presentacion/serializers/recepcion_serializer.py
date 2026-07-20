from rest_framework import serializers
from dominio.models import Recepcion


class RecepcionSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='producto.nombre',
        read_only=True
    )
    producto_isbn = serializers.CharField(
        source='producto.isbn',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.razon_social',
        read_only=True
    )
    proveedor_ruc = serializers.CharField(
        source='proveedor.ruc',
        read_only=True
    )

    class Meta:
        model = Recepcion
        fields = [
            'id',
            'numero_recepcion',
            'orden_compra',
            'producto',
            'producto_nombre',
            'producto_isbn',
            'proveedor',
            'proveedor_nombre',
            'proveedor_ruc',
            'cantidad_esperada',
            'cantidad_recibida',
            'cantidad_verificada',
            'cantidad_conforme',
            'cantidad_no_conforme',
            'fecha_recepcion',
            'fecha_verificacion',
            'fecha_confirmacion',
            'fecha_esperada_entrega',
            'estado',
            'conformidad',
            'observaciones',
            'creado_por',
            'verificado_por',
            'confirmado_por',
        ]
        read_only_fields = [
            'id',
            'numero_recepcion',
            'fecha_recepcion',
            'fecha_verificacion',
            'fecha_confirmacion',
            'cantidad_verificada',
            'cantidad_conforme',
            'cantidad_no_conforme',
            'estado',
            'conformidad',
            'verificado_por',
            'confirmado_por',
        ]


class RecepcionListSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='producto.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.razon_social',
        read_only=True
    )

    class Meta:
        model = Recepcion
        fields = [
            'id',
            'numero_recepcion',
            'orden_compra',
            'producto_nombre',
            'proveedor_nombre',
            'cantidad_esperada',
            'cantidad_recibida',
            'fecha_recepcion',
            'fecha_esperada_entrega',
            'estado',
            'conformidad',
        ]

"""
Serializador para Productos
Integrante 1 - Gestión de Productos
"""
from decimal import Decimal
from rest_framework import serializers
from dominio.models import Producto, Proveedor


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializador para la entidad Producto
    """
    
    # ========== CAMPOS CALCULADOS (Solo lectura) ==========
    tiene_stock_bajo = serializers.BooleanField(read_only=True)
    valor_inventario = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    margen_ganancia = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    estado_stock = serializers.CharField(read_only=True)
    ganancia_por_unidad = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    # ========== CAMPOS RELACIONADOS ==========
    proveedor_nombre = serializers.CharField(
        source='proveedor_principal.razon_social',
        read_only=True
    )
    proveedor_ruc = serializers.CharField(
        source='proveedor_principal.ruc',
        read_only=True
    )
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'isbn',
            'nombre',
            'descripcion',
            'tipo',
            'categoria',
            'editorial',
            'autor',
            'año_publicacion',
            'precio_compra',
            'precio_venta',
            'iva',
            'stock_actual',
            'stock_minimo',
            'stock_maximo',
            'ubicacion',
            'pasillo',
            'estante',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
            'proveedor_principal',
            'proveedor_nombre',
            'proveedor_ruc',
            # Campos calculados (SOLO los que existen)
            'tiene_stock_bajo',
            'valor_inventario',
            'margen_ganancia',
            'estado_stock',
            'ganancia_por_unidad'
        ]
        read_only_fields = [
            'id',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
    
    # ========== VALIDACIONES ==========
    def validate_isbn(self, value):
        if self.instance:
            if Producto.objects.filter(isbn=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(f"Ya existe un producto con el ISBN '{value}'")
        else:
            if Producto.objects.filter(isbn=value).exists():
                raise serializers.ValidationError(f"Ya existe un producto con el ISBN '{value}'")
        return value
    
    def validate_precio_venta(self, value):
        precio_compra = self.initial_data.get('precio_compra')
        if precio_compra and value <= Decimal(str(precio_compra)):
            raise serializers.ValidationError("El precio de venta debe ser mayor al precio de compra")
        return value
    
    def validate_stock_maximo(self, value):
        stock_minimo = self.initial_data.get('stock_minimo')
        if stock_minimo and value < int(stock_minimo):
            raise serializers.ValidationError("El stock máximo debe ser mayor al stock mínimo")
        return value


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listar productos"""
    estado_stock = serializers.CharField(read_only=True)
    proveedor_nombre = serializers.CharField(
        source='proveedor_principal.razon_social',
        read_only=True
    )
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'isbn',
            'nombre',
            'categoria',
            'tipo',
            'stock_actual',
            'estado_stock',
            'proveedor_nombre',
            'precio_venta',
            'activo'
        ]


class ProductoStockSerializer(serializers.ModelSerializer):
    """Serializador para operaciones de stock"""
    tiene_stock_bajo = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'isbn',
            'nombre',
            'stock_actual',
            'stock_minimo',
            'stock_maximo',
            'tiene_stock_bajo'
        ]
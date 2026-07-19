"""
Vistas (Controladores) para Productos con ViewSet
Integrante 1 - Gestión de Productos
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from aplicacion.services.producto_service import ProductoService
from presentacion.serializers.producto_serializer import (
    ProductoSerializer,
    ProductoListSerializer,
    ProductoStockSerializer
)


class ProductoViewSet(viewsets.ViewSet):
    """
    ViewSet para el servicio de Productos
    """
    
    def list(self, request):
        """GET /api/productos/"""
        try:
            filtros = {
                'categoria': request.query_params.get('categoria'),
                'tipo': request.query_params.get('tipo'),
                'stock_bajo': request.query_params.get('stock_bajo'),
                'search': request.query_params.get('search'),
                'proveedor_id': request.query_params.get('proveedor_id'),
            }
            filtros = {k: v for k, v in filtros.items() if v is not None}
            
            productos = ProductoService.listar_productos(filtros)
            
            if request.query_params.get('format') == 'simple':
                serializer = ProductoListSerializer(productos, many=True)
            else:
                serializer = ProductoSerializer(productos, many=True)
            
            return Response({
                'count': productos.count(),
                'results': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request):
        """POST /api/productos/"""
        try:
            producto = ProductoService.crear_producto(request.data)
            serializer = ProductoSerializer(producto)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def retrieve(self, request, pk=None):
        """GET /api/productos/{id}/"""
        producto = ProductoService.obtener_producto_por_id(pk)
        if not producto:
            return Response(
                {'error': f'Producto con ID {pk} no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProductoSerializer(producto)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """PUT /api/productos/{id}/"""
        try:
            producto = ProductoService.actualizar_producto(pk, request.data)
            serializer = ProductoSerializer(producto)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, pk=None):
        """DELETE /api/productos/{id}/"""
        eliminado = ProductoService.eliminar_producto(pk)
        if not eliminado:
            return Response(
                {'error': f'Producto con ID {pk} no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {'message': 'Producto eliminado exitosamente'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """GET /api/productos/buscar/?isbn=xxx"""
        isbn = request.query_params.get('isbn')
        
        if not isbn:
            return Response(
                {'error': 'El parámetro "isbn" es obligatorio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        producto = ProductoService.obtener_producto_por_isbn(isbn)
        if not producto:
            return Response(
                {'error': f'Producto con ISBN "{isbn}" no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProductoSerializer(producto)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def stock(self, request, pk=None):
        """PATCH /api/productos/{id}/stock/"""
        try:
            cantidad = request.data.get('cantidad')
            operacion = request.data.get('operacion', 'incrementar')
            
            if cantidad is None:
                return Response(
                    {'error': 'El campo "cantidad" es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            producto = ProductoService.actualizar_stock(
                pk,
                int(cantidad),
                operacion
            )
            serializer = ProductoStockSerializer(producto)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['patch'])
    def precios(self, request, pk=None):
        """PATCH /api/productos/{id}/precios/"""
        try:
            precio_compra = request.data.get('precio_compra')
            precio_venta = request.data.get('precio_venta')
            
            if precio_compra is None or precio_venta is None:
                return Response(
                    {'error': 'Los campos "precio_compra" y "precio_venta" son obligatorios'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            producto = ProductoService.actualizar_precios(
                pk,
                precio_compra,
                precio_venta
            )
            serializer = ProductoSerializer(producto)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['patch'])
    def activar(self, request, pk=None):
        """PATCH /api/productos/{id}/activar/"""
        try:
            producto = ProductoService.activar_producto(pk)
            serializer = ProductoSerializer(producto)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def alertas_stock_bajo(self, request):
        """GET /api/productos/alertas_stock_bajo/"""
        alerta = ProductoService.generar_alerta_stock_bajo()
        return Response(alerta)
    
    @action(detail=False, methods=['get'])
    def valor_inventario(self, request):
        """GET /api/productos/valor_inventario/"""
        reporte = ProductoService.calcular_valor_total_inventario()
        return Response(reporte)
    
    @action(detail=False, methods=['get'])
    def categoria(self, request):
        """GET /api/productos/categoria/?nombre=xxx"""
        categoria = request.query_params.get('nombre')
        
        if not categoria:
            return Response(
                {'error': 'El parámetro "nombre" es obligatorio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        productos = ProductoService.listar_productos_por_categoria(categoria)
        serializer = ProductoListSerializer(productos, many=True)
        return Response({
            'categoria': categoria,
            'count': productos.count(),
            'results': serializer.data
        })
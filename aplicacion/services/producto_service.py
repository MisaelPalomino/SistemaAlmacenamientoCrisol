"""
Servicio de Aplicación para Productos
Integrante 1 - Gestión de Productos
"""
from django.db import transaction
from django.db.models import Q, F
from decimal import Decimal
from dominio.models import Producto, Proveedor


class ProductoService:
    """
    Servicio para la gestión de productos en el inventario
    Proporciona operaciones CRUD y funcionalidades específicas
    """
    
    # ========== CREAR ==========
    @staticmethod
    def crear_producto(data):
        """
        Crea un nuevo producto en el sistema
        Args:
            data: Diccionario con los datos del producto
        Returns:
            Producto: El producto creado
        Raises:
            ValueError: Si hay errores de validación
        """
        try:
            # Validar que el proveedor existe si se envía
            if data.get('proveedor_principal_id'):
                proveedor = Proveedor.objects.get(
                    id=data['proveedor_principal_id'],
                    activo=True
                )
                data['proveedor_principal'] = proveedor
            
            producto = Producto(**data)
            producto.full_clean()
            producto.save()
            return producto
            
        except Proveedor.DoesNotExist:
            raise ValueError(f"Proveedor con ID {data.get('proveedor_principal_id')} no encontrado")
        except Exception as e:
            raise ValueError(f"Error al crear producto: {str(e)}")
    
    # ========== LEER ==========
    @staticmethod
    def listar_productos(filtros=None):
        """
        Lista todos los productos activos con filtros opcionales
        Args:
            filtros: Diccionario con filtros (categoria, tipo, stock_bajo, search, proveedor_id)
        Returns:
            QuerySet: Lista de productos filtrados
        """
        queryset = Producto.objects.filter(activo=True)
        
        if filtros:
            # Filtro por categoría
            if filtros.get('categoria'):
                queryset = queryset.filter(categoria=filtros['categoria'])
            
            # Filtro por tipo
            if filtros.get('tipo'):
                queryset = queryset.filter(tipo=filtros['tipo'])
            
            # Filtro por stock bajo
            if filtros.get('stock_bajo') == 'true':
                queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))
            
            # Filtro por stock excedente
            if filtros.get('stock_excedente') == 'true':
                queryset = queryset.filter(stock_actual__gte=F('stock_maximo'))
            
            # Búsqueda por nombre, ISBN o autor
            if filtros.get('search'):
                search = filtros['search']
                queryset = queryset.filter(
                    Q(nombre__icontains=search) |
                    Q(isbn__icontains=search) |
                    Q(autor__icontains=search)
                )
            
            # Filtro por proveedor
            if filtros.get('proveedor_id'):
                queryset = queryset.filter(proveedor_principal_id=filtros['proveedor_id'])
        
        return queryset.order_by('nombre')
    
    @staticmethod
    def obtener_producto_por_id(producto_id):
        """
        Obtiene un producto por su ID
        Args:
            producto_id: ID del producto
        Returns:
            Producto o None si no existe
        """
        try:
            return Producto.objects.get(id=producto_id, activo=True)
        except Producto.DoesNotExist:
            return None
    
    @staticmethod
    def obtener_producto_por_isbn(isbn):
        """
        Obtiene un producto por su ISBN/SKU
        Args:
            isbn: ISBN o SKU del producto
        Returns:
            Producto o None si no existe
        """
        try:
            return Producto.objects.get(isbn=isbn, activo=True)
        except Producto.DoesNotExist:
            return None
    
    @staticmethod
    def listar_productos_por_categoria(categoria):
        """
        Lista productos por categoría
        Args:
            categoria: Categoría a filtrar
        Returns:
            QuerySet: Productos de la categoría
        """
        return Producto.objects.filter(categoria=categoria, activo=True)
    
    @staticmethod
    def listar_productos_con_stock_bajo():
        """
        Lista productos con stock bajo (stock_actual <= stock_minimo)
        Returns:
            QuerySet: Productos con stock bajo
        """
        return Producto.objects.filter(
            stock_actual__lte=F('stock_minimo'),
            activo=True
        )
    
    @staticmethod
    def listar_productos_con_stock_excedente():
        """
        Lista productos con stock excedente (stock_actual >= stock_maximo)
        Returns:
            QuerySet: Productos con stock excedente
        """
        return Producto.objects.filter(
            stock_actual__gte=F('stock_maximo'),
            activo=True
        )
    
    # ========== ACTUALIZAR ==========
    @staticmethod
    def actualizar_producto(producto_id, data):
        """
        Actualiza un producto existente
        Args:
            producto_id: ID del producto a actualizar
            data: Diccionario con los datos a actualizar
        Returns:
            Producto: El producto actualizado
        Raises:
            ValueError: Si el producto no existe o hay errores de validación
        """
        try:
            producto = Producto.objects.get(id=producto_id)

            # Validar que el proveedor existe si se envía
            if data.get('proveedor_principal_id'):
                proveedor = Proveedor.objects.get(
                    id=data['proveedor_principal_id'],
                    activo=True
                )
                producto.proveedor_principal = proveedor

            for key, value in data.items():
                if key != 'proveedor_principal_id':  # Evitar conflicto
                    setattr(producto, key, value)
            
            producto.full_clean()
            producto.save()
            return producto
            
        except Producto.DoesNotExist:
            raise ValueError(f"Producto con ID {producto_id} no encontrado")
        except Proveedor.DoesNotExist:
            raise ValueError(f"Proveedor con ID {data.get('proveedor_principal_id')} no encontrado")
        except Exception as e:
            raise ValueError(f"Error al actualizar producto: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def actualizar_stock(producto_id, cantidad, operacion='incrementar'):
        """
        Actualiza el stock de un producto
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a incrementar/decrementar
            operacion: 'incrementar' o 'decrementar'
        Returns:
            Producto: El producto con stock actualizado
        Raises:
            ValueError: Si el producto no existe o hay errores
        """
        try:
            producto = Producto.objects.get(id=producto_id, activo=True)
            
            if operacion == 'incrementar':
                producto.incrementar_stock(cantidad)
            elif operacion == 'decrementar':
                producto.decrementar_stock(cantidad)
            else:
                raise ValueError("Operación inválida. Use 'incrementar' o 'decrementar'")
            
            return producto
            
        except Producto.DoesNotExist:
            raise ValueError(f"Producto con ID {producto_id} no encontrado")
        except ValueError as e:
            raise ValueError(str(e))
    
    @staticmethod
    @transaction.atomic
    def actualizar_precios(producto_id, nuevo_precio_compra, nuevo_precio_venta):
        """
        Actualiza los precios de un producto
        Args:
            producto_id: ID del producto
            nuevo_precio_compra: Nuevo precio de compra
            nuevo_precio_venta: Nuevo precio de venta
        Returns:
            Producto: El producto con precios actualizados
        """
        try:
            producto = Producto.objects.get(id=producto_id, activo=True)
            producto.actualizar_precios(
                Decimal(str(nuevo_precio_compra)),
                Decimal(str(nuevo_precio_venta))
            )
            return producto
            
        except Producto.DoesNotExist:
            raise ValueError(f"Producto con ID {producto_id} no encontrado")
        except ValueError as e:
            raise ValueError(str(e))
    
    # ========== ELIMINAR ==========
    @staticmethod
    def eliminar_producto(producto_id):
        """
        Elimina lógicamente un producto (desactivación)
        Args:
            producto_id: ID del producto a eliminar
        Returns:
            bool: True si se eliminó, False si no existe
        """
        try:
            producto = Producto.objects.get(id=producto_id)
            producto.activo = False
            producto.save()
            return True
        except Producto.DoesNotExist:
            return False
    
    @staticmethod
    def activar_producto(producto_id):
        """
        Activa un producto previamente desactivado
        Args:
            producto_id: ID del producto a activar
        Returns:
            Producto: El producto activado
        Raises:
            ValueError: Si el producto no existe
        """
        try:
            producto = Producto.objects.get(id=producto_id, activo=False)
            producto.activo = True
            producto.save()
            return producto
        except Producto.DoesNotExist:
            raise ValueError(f"Producto con ID {producto_id} no encontrado o ya está activo")
    
    # ========== REPORTES Y ALERTAS ==========
    @staticmethod
    def generar_alerta_stock_bajo():
        """
        Genera un reporte de productos con stock bajo
        Returns:
            dict: Resumen de productos con stock bajo
        """
        productos_bajo = ProductoService.listar_productos_con_stock_bajo()
        
        if productos_bajo.exists():
            return {
                'alerta': True,
                'mensaje': '⚠️ Productos con stock bajo detectados',
                'total': productos_bajo.count(),
                'productos': [
                    {
                        'id': p.id,
                        'nombre': p.nombre,
                        'isbn': p.isbn,
                        'stock_actual': p.stock_actual,
                        'stock_minimo': p.stock_minimo,
                        'categoria': p.categoria
                    } for p in productos_bajo
                ]
            }
        return {
            'alerta': False,
            'mensaje': '✅ Todos los productos tienen stock adecuado',
            'total': 0
        }
    
    @staticmethod
    def calcular_valor_total_inventario():
        """
        Calcula el valor total del inventario
        Returns:
            dict: Resumen del valor del inventario
        """
        productos = Producto.objects.filter(activo=True)
        valor_total = sum(p.valor_inventario for p in productos)
        
        return {
            'total_productos': productos.count(),
            'valor_total_inventario': float(valor_total),
            'productos_con_stock': productos.filter(stock_actual__gt=0).count(),
            'productos_agotados': productos.filter(stock_actual=0).count()
        }
    
    @staticmethod
    def contar_productos(filtros=None):
        """
        Cuenta la cantidad de productos que cumplen los filtros
        Args:
            filtros: Diccionario con filtros
        Returns:
            int: Cantidad de productos
        """
        queryset = Producto.objects.filter(activo=True)
        
        if filtros:
            if filtros.get('categoria'):
                queryset = queryset.filter(categoria=filtros['categoria'])
            if filtros.get('stock_bajo') == 'true':
                queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))
        
        return queryset.count()
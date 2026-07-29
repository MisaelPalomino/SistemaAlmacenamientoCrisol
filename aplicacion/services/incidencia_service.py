"""
Servicio de Aplicación para Incidencias
Integrante 4 - Gestión de Incidencias
"""
from django.db import transaction
from django.db.models import Q
from dominio.models import Incidencia, Producto, Recepcion


class IncidenciaService:
    """
    Servicio para la gestión de incidencias de inventario
    """
    
    # ========== CREAR ==========
    @staticmethod
    def crear_incidencia(data):
        """
        Registra una nueva incidencia
        Args:
            data: Diccionario con los datos de la incidencia
        Returns:
            Incidencia: La incidencia creada
        """
        try:
            # Validar que el producto existe
            producto_id = data.get('producto_id')
            if producto_id:
                producto = Producto.objects.get(id=producto_id, activo=True)
            
            # Validar que la recepción existe (si se proporciona)
            recepcion_id = data.get('recepcion_id')
            if recepcion_id:
                recepcion = Recepcion.objects.get(id=recepcion_id)
            
            incidencia = Incidencia(**data)
            incidencia.full_clean()
            incidencia.save()
            return incidencia
            
        except Producto.DoesNotExist:
            raise ValueError(f"Producto con ID {producto_id} no encontrado")
        except Recepcion.DoesNotExist:
            raise ValueError(f"Recepción con ID {recepcion_id} no encontrada")
        except Exception as e:
            raise ValueError(f"Error al crear incidencia: {str(e)}")
    
    # ========== LEER ==========
    @staticmethod
    def listar_incidencias(filtros=None):
        """
        Lista todas las incidencias con filtros opcionales
        Args:
            filtros: Diccionario con filtros (tipo, estado, prioridad, producto_id)
        Returns:
            QuerySet: Lista de incidencias filtradas
        """
        queryset = Incidencia.objects.all()
        
        if filtros:
            if filtros.get('tipo'):
                queryset = queryset.filter(tipo=filtros['tipo'])
            if filtros.get('estado'):
                queryset = queryset.filter(estado=filtros['estado'])
            if filtros.get('prioridad'):
                queryset = queryset.filter(prioridad=filtros['prioridad'])
            if filtros.get('producto_id'):
                queryset = queryset.filter(producto_id=filtros['producto_id'])
            if filtros.get('search'):
                search = filtros['search']
                queryset = queryset.filter(
                    Q(codigo_incidencia__icontains=search) |
                    Q(descripcion__icontains=search)
                )
        
        return queryset.order_by('-fecha_registro')
    
    @staticmethod
    def obtener_incidencia_por_id(incidencia_id):
        """
        Obtiene una incidencia por su ID
        Args:
            incidencia_id: ID de la incidencia
        Returns:
            Incidencia o None si no existe
        """
        try:
            return Incidencia.objects.get(id=incidencia_id)
        except Incidencia.DoesNotExist:
            return None
    
    @staticmethod
    def obtener_incidencia_por_codigo(codigo):
        """
        Obtiene una incidencia por su código
        Args:
            codigo: Código de la incidencia
        Returns:
            Incidencia o None si no existe
        """
        try:
            return Incidencia.objects.get(codigo_incidencia=codigo)
        except Incidencia.DoesNotExist:
            return None
    
    @staticmethod
    def listar_incidencias_activas():
        """
        Lista incidencias activas (no cerradas)
        Returns:
            QuerySet: Incidencias activas
        """
        return Incidencia.objects.exclude(estado='CERRADA').order_by('-fecha_registro')
    
    @staticmethod
    def listar_incidencias_por_producto(producto_id):
        """
        Lista incidencias de un producto específico
        Args:
            producto_id: ID del producto
        Returns:
            QuerySet: Incidencias del producto
        """
        return Incidencia.objects.filter(producto_id=producto_id).order_by('-fecha_registro')
    
    # ========== ACTUALIZAR ==========
    @staticmethod
    @transaction.atomic
    def asignar_incidencia(incidencia_id, asignado_a):
        """
        Asigna una incidencia a un responsable
        Args:
            incidencia_id: ID de la incidencia
            asignado_a: Persona asignada
        Returns:
            Incidencia: La incidencia actualizada
        """
        try:
            incidencia = Incidencia.objects.get(id=incidencia_id)
            incidencia.asignar(asignado_a)
            return incidencia
        except Incidencia.DoesNotExist:
            raise ValueError(f"Incidencia con ID {incidencia_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))
    
    @staticmethod
    @transaction.atomic
    def clasificar_incidencia(incidencia_id, nueva_prioridad):
        """
        Clasifica o reclasifica una incidencia
        Args:
            incidencia_id: ID de la incidencia
            nueva_prioridad: Nueva prioridad (BAJA, MEDIA, ALTA, CRITICA)
        Returns:
            Incidencia: La incidencia actualizada
        """
        try:
            incidencia = Incidencia.objects.get(id=incidencia_id)
            incidencia.clasificar(nueva_prioridad)
            return incidencia
        except Incidencia.DoesNotExist:
            raise ValueError(f"Incidencia con ID {incidencia_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))
    
    @staticmethod
    @transaction.atomic
    def resolver_incidencia(incidencia_id, solucion):
        """
        Resuelve una incidencia
        Args:
            incidencia_id: ID de la incidencia
            solucion: Descripción de la solución aplicada
        Returns:
            Incidencia: La incidencia resuelta
        """
        try:
            incidencia = Incidencia.objects.get(id=incidencia_id)
            incidencia.resolver(solucion)
            return incidencia
        except Incidencia.DoesNotExist:
            raise ValueError(f"Incidencia con ID {incidencia_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))
    
    @staticmethod
    @transaction.atomic
    def cerrar_incidencia(incidencia_id):
        """
        Cierra una incidencia definitivamente
        Args:
            incidencia_id: ID de la incidencia
        Returns:
            Incidencia: La incidencia cerrada
        """
        try:
            incidencia = Incidencia.objects.get(id=incidencia_id)
            incidencia.cerrar()
            return incidencia
        except Incidencia.DoesNotExist:
            raise ValueError(f"Incidencia con ID {incidencia_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))
    
    @staticmethod
    def agregar_observacion(incidencia_id, observacion):
        """
        Agrega una observación a la incidencia
        Args:
            incidencia_id: ID de la incidencia
            observacion: Observación a agregar
        Returns:
            Incidencia: La incidencia actualizada
        """
        try:
            incidencia = Incidencia.objects.get(id=incidencia_id)
            incidencia.agregar_observacion(observacion)
            return incidencia
        except Incidencia.DoesNotExist:
            raise ValueError(f"Incidencia con ID {incidencia_id} no encontrada")
    
    # ========== REPORTES ==========
    @staticmethod
    def resumen_incidencias():
        """
        Genera un resumen de incidencias
        Returns:
            dict: Resumen de incidencias por estado y prioridad
        """
        total = Incidencia.objects.count()
        activas = Incidencia.objects.exclude(estado='CERRADA').count()
        cerradas = Incidencia.objects.filter(estado='CERRADA').count()
        criticas = Incidencia.objects.filter(prioridad='CRITICA').count()
        
        return {
            'total_incidencias': total,
            'activas': activas,
            'cerradas': cerradas,
            'criticas': criticas,
            'por_estado': {
                estado: Incidencia.objects.filter(estado=estado).count()
                for estado, _ in Incidencia.ESTADOS
            },
            'por_prioridad': {
                prioridad: Incidencia.objects.filter(prioridad=prioridad).count()
                for prioridad, _ in Incidencia.PRIORIDADES
            }
        }
    
    @staticmethod
    def listar_tipos():
        """
        Retorna la lista de tipos de incidencia disponibles
        Returns:
            list: Lista de tuplas (código, descripción)
        """
        return Incidencia.TIPOS
    
    @staticmethod
    def listar_prioridades():
        """
        Retorna la lista de prioridades disponibles
        Returns:
            list: Lista de tuplas (código, descripción)
        """
        return Incidencia.PRIORIDADES
    
    @staticmethod
    def listar_estados():
        """
        Retorna la lista de estados disponibles
        Returns:
            list: Lista de tuplas (código, descripción)
        """
        return Incidencia.ESTADOS
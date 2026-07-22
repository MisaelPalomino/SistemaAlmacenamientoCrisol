"""
Servicio de Aplicación para Solicitudes de Reposición
Integrante 5 - Gestión de Reposiciones
"""

from django.db import transaction
from django.db.models import Q
from dominio.models import SolicitudReposicion, Producto


class ReposicionService:
    """
    Servicio para la gestión de solicitudes de reposición
    """

    # ========== CREAR ==========
    @staticmethod
    def crear_solicitud(data):
        """
        Crea una nueva solicitud de reposición
        Args:
            data: Diccionario con los datos de la solicitud
        Returns:
            SolicitudReposicion: La solicitud creada
        """
        try:
            # Verificar que el producto existe
            producto_id = data.get("producto_id")
            if producto_id:
                producto = Producto.objects.get(id=producto_id, activo=True)

            solicitud = SolicitudReposicion(**data)
            solicitud.full_clean()
            solicitud.save()
            return solicitud

        except Producto.DoesNotExist:
            raise ValueError(f"Producto con ID {producto_id} no encontrado")
        except Exception as e:
            raise ValueError(f"Error al crear solicitud: {str(e)}")

    # ========== LEER ==========
    @staticmethod
    def listar_solicitudes(filtros=None):
        """
        Lista todas las solicitudes con filtros opcionales
        Args:
            filtros: Diccionario con filtros (estado, prioridad, producto_id)
        Returns:
            QuerySet: Lista de solicitudes filtradas
        """
        queryset = SolicitudReposicion.objects.all()

        if filtros:
            if filtros.get("estado"):
                queryset = queryset.filter(estado=filtros["estado"])
            if filtros.get("prioridad"):
                queryset = queryset.filter(prioridad=filtros["prioridad"])
            if filtros.get("producto_id"):
                queryset = queryset.filter(producto_id=filtros["producto_id"])
            if filtros.get("search"):
                search = filtros["search"]
                queryset = queryset.filter(
                    Q(numero_solicitud__icontains=search) | Q(motivo__icontains=search)
                )

        return queryset.order_by("-fecha_solicitud")

    @staticmethod
    def obtener_solicitud_por_id(solicitud_id):
        """
        Obtiene una solicitud por su ID
        Args:
            solicitud_id: ID de la solicitud
        Returns:
            SolicitudReposicion o None si no existe
        """
        try:
            return SolicitudReposicion.objects.get(id=solicitud_id)
        except SolicitudReposicion.DoesNotExist:
            return None

    @staticmethod
    def obtener_solicitud_por_numero(numero_solicitud):
        """
        Obtiene una solicitud por su número
        Args:
            numero_solicitud: Número de la solicitud
        Returns:
            SolicitudReposicion o None si no existe
        """
        try:
            return SolicitudReposicion.objects.get(numero_solicitud=numero_solicitud)
        except SolicitudReposicion.DoesNotExist:
            return None

    @staticmethod
    def listar_solicitudes_pendientes():
        """
        Lista solicitudes pendientes de aprobación
        Returns:
            QuerySet: Solicitudes en estado CREADA o EN_REVISION
        """
        return SolicitudReposicion.objects.filter(
            estado__in=["CREADA", "EN_REVISION"]
        ).order_by("-fecha_solicitud")

    @staticmethod
    def listar_solicitudes_por_producto(producto_id):
        """
        Lista solicitudes de un producto específico
        Args:
            producto_id: ID del producto
        Returns:
            QuerySet: Solicitudes del producto
        """
        return SolicitudReposicion.objects.filter(producto_id=producto_id).order_by(
            "-fecha_solicitud"
        )

    # ========== ACTUALIZAR ==========
    @staticmethod
    @transaction.atomic
    def aprobar_solicitud(solicitud_id, aprobado_por, cantidad_aprobada=None):
        """
        Aprueba una solicitud de reposición
        Args:
            solicitud_id: ID de la solicitud
            aprobado_por: Persona que aprueba
            cantidad_aprobada: Cantidad aprobada (opcional)
        Returns:
            SolicitudReposicion: La solicitud aprobada
        """
        try:
            solicitud = SolicitudReposicion.objects.get(id=solicitud_id)
            solicitud.aprobar(aprobado_por, cantidad_aprobada)
            return solicitud
        except SolicitudReposicion.DoesNotExist:
            raise ValueError(f"Solicitud con ID {solicitud_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))

    @staticmethod
    @transaction.atomic
    def ejecutar_reposicion(solicitud_id, ejecutado_por):
        """
        Ejecuta una reposición
        Args:
            solicitud_id: ID de la solicitud
            ejecutado_por: Persona que ejecuta
        Returns:
            SolicitudReposicion: La solicitud en ejecución
        """
        try:
            solicitud = SolicitudReposicion.objects.get(id=solicitud_id)
            solicitud.ejecutar(ejecutado_por)
            return solicitud
        except SolicitudReposicion.DoesNotExist:
            raise ValueError(f"Solicitud con ID {solicitud_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))

    @staticmethod
    @transaction.atomic
    def completar_reposicion(solicitud_id, cantidad_repuesta):
        """
        Completa una reposición y actualiza stock
        Args:
            solicitud_id: ID de la solicitud
            cantidad_repuesta: Cantidad realmente repuesta
        Returns:
            SolicitudReposicion: La solicitud completada
        """
        try:
            solicitud = SolicitudReposicion.objects.get(id=solicitud_id)
            solicitud.completar(cantidad_repuesta)
            return solicitud
        except SolicitudReposicion.DoesNotExist:
            raise ValueError(f"Solicitud con ID {solicitud_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))

    @staticmethod
    def cancelar_solicitud(solicitud_id, motivo):
        """
        Cancela una solicitud
        Args:
            solicitud_id: ID de la solicitud
            motivo: Razón de la cancelación
        Returns:
            SolicitudReposicion: La solicitud cancelada
        """
        try:
            solicitud = SolicitudReposicion.objects.get(id=solicitud_id)
            solicitud.cancelar(motivo)
            return solicitud
        except SolicitudReposicion.DoesNotExist:
            raise ValueError(f"Solicitud con ID {solicitud_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))

    @staticmethod
    def enviar_revision(solicitud_id):
        """
        Envía una solicitud a revisión
        Args:
            solicitud_id: ID de la solicitud
        Returns:
            SolicitudReposicion: La solicitud en revisión
        """
        try:
            solicitud = SolicitudReposicion.objects.get(id=solicitud_id)
            solicitud.enviar_revision()
            return solicitud
        except SolicitudReposicion.DoesNotExist:
            raise ValueError(f"Solicitud con ID {solicitud_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))

    # ========== REPORTES ==========
    @staticmethod
    def resumen_solicitudes():
        """
        Genera un resumen de todas las solicitudes
        Returns:
            dict: Resumen de solicitudes
        """
        total = SolicitudReposicion.objects.count()
        pendientes = SolicitudReposicion.objects.filter(
            estado__in=["CREADA", "EN_REVISION"]
        ).count()
        aprobadas = SolicitudReposicion.objects.filter(estado="APROBADA").count()
        completadas = SolicitudReposicion.objects.filter(estado="COMPLETADA").count()
        canceladas = SolicitudReposicion.objects.filter(estado="CANCELADA").count()

        return {
            "total_solicitudes": total,
            "pendientes": pendientes,
            "aprobadas": aprobadas,
            "completadas": completadas,
            "canceladas": canceladas,
        }

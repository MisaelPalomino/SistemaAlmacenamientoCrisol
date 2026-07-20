from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from dominio.models import Proveedor


class ProveedorService:
    CALIFICACIONES_VALIDAS = {"A", "B", "C", "D"}

    @staticmethod
    def _normalizar_ruc(ruc):
        if ruc is None:
            raise ValueError("El RUC es obligatorio")

        ruc_normalizado = str(ruc).strip()
        if len(ruc_normalizado) != 11 or not ruc_normalizado.isdigit():
            raise ValueError("El RUC debe contener exactamente 11 dígitos")

        return ruc_normalizado

    @classmethod
    def _validar_calificacion(cls, calificacion):
        if calificacion is None:
            return None

        calificacion_normalizada = str(calificacion).strip().upper()
        if calificacion_normalizada not in cls.CALIFICACIONES_VALIDAS:
            raise ValueError("La calificación debe ser A, B, C o D")

        return calificacion_normalizada

    @staticmethod
    def _mensaje_validacion(error):
        if hasattr(error, "message_dict"):
            mensajes = []
            for campo, errores in error.message_dict.items():
                mensajes.append(f"{campo}: {', '.join(errores)}")
            return "; ".join(mensajes)

        return "; ".join(error.messages)

    @classmethod
    @transaction.atomic
    def crear_proveedor(cls, data):
        datos = dict(data)
        ruc = cls._normalizar_ruc(datos.get("ruc"))
        datos["ruc"] = ruc

        if Proveedor.objects.filter(ruc=ruc).exists():
            raise ValueError(f"Ya existe un proveedor con el RUC {ruc}")

        if "calificacion" in datos:
            datos["calificacion"] = cls._validar_calificacion(
                datos["calificacion"]
            )

        try:
            proveedor = Proveedor(**datos)
            proveedor.full_clean()
            proveedor.save()
            return proveedor
        except ValidationError as error:
            raise ValueError(cls._mensaje_validacion(error)) from error
        except IntegrityError as error:
            raise ValueError(f"Ya existe un proveedor con el RUC {ruc}") from error

    @classmethod
    def listar_proveedores(cls, filtros=None):
        queryset = Proveedor.objects.filter(activo=True)

        if filtros and filtros.get("calificacion"):
            calificacion = cls._validar_calificacion(filtros["calificacion"])
            queryset = queryset.filter(calificacion=calificacion)

        return queryset.order_by("razon_social")

    @staticmethod
    def obtener_proveedor_por_id(proveedor_id):
        try:
            return Proveedor.objects.get(id=proveedor_id, activo=True)
        except (Proveedor.DoesNotExist, TypeError, ValueError):
            return None

    @classmethod
    def buscar_proveedor_por_ruc(cls, ruc):
        ruc_normalizado = cls._normalizar_ruc(ruc)
        try:
            return Proveedor.objects.get(ruc=ruc_normalizado, activo=True)
        except Proveedor.DoesNotExist:
            return None

    obtener_proveedor_por_ruc = buscar_proveedor_por_ruc

    @classmethod
    @transaction.atomic
    def actualizar_proveedor(cls, proveedor_id, data):
        try:
            proveedor = Proveedor.objects.select_for_update().get(
                id=proveedor_id,
                activo=True,
            )
        except Proveedor.DoesNotExist as error:
            raise ValueError(
                f"Proveedor activo con ID {proveedor_id} no encontrado"
            ) from error

        datos = dict(data)

        if "ruc" in datos:
            nuevo_ruc = cls._normalizar_ruc(datos["ruc"])
            ruc_duplicado = Proveedor.objects.filter(ruc=nuevo_ruc).exclude(
                id=proveedor.id
            )
            if ruc_duplicado.exists():
                raise ValueError(f"Ya existe un proveedor con el RUC {nuevo_ruc}")
            datos["ruc"] = nuevo_ruc

        if "calificacion" in datos:
            datos["calificacion"] = cls._validar_calificacion(
                datos["calificacion"]
            )

        for campo_protegido in (
            "id",
            "activo",
            "fecha_registro",
            "fecha_actualizacion",
        ):
            datos.pop(campo_protegido, None)

        for campo, valor in datos.items():
            if not hasattr(proveedor, campo):
                raise ValueError(f"El campo '{campo}' no pertenece al proveedor")
            setattr(proveedor, campo, valor)

        try:
            proveedor.full_clean()
            proveedor.save()
            return proveedor
        except ValidationError as error:
            raise ValueError(cls._mensaje_validacion(error)) from error
        except IntegrityError as error:
            raise ValueError(
                f"Ya existe un proveedor con el RUC {proveedor.ruc}"
            ) from error

    @classmethod
    def actualizar_calificacion(cls, proveedor_id, calificacion):
        return cls.actualizar_proveedor(
            proveedor_id,
            {"calificacion": cls._validar_calificacion(calificacion)},
        )

    @staticmethod
    @transaction.atomic
    def desactivar_proveedor(proveedor_id):
        try:
            proveedor = Proveedor.objects.select_for_update().get(
                id=proveedor_id,
                activo=True,
            )
        except Proveedor.DoesNotExist:
            return False

        proveedor.activo = False
        proveedor.save(update_fields=["activo", "fecha_actualizacion"])
        return True

    @staticmethod
    @transaction.atomic
    def activar_proveedor(proveedor_id):
        try:
            proveedor = Proveedor.objects.select_for_update().get(
                id=proveedor_id,
                activo=False,
            )
        except Proveedor.DoesNotExist as error:
            raise ValueError(
                f"Proveedor con ID {proveedor_id} no encontrado o ya está activo"
            ) from error

        proveedor.activo = True
        proveedor.save(update_fields=["activo", "fecha_actualizacion"])
        return proveedor

    eliminar_proveedor = desactivar_proveedor

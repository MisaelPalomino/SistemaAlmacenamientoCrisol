from django.db import transaction
from django.utils import timezone
from dominio.models import Recepcion, Producto, Proveedor


class RecepcionService:

    @staticmethod
    def generar_numero_recepcion():
        ahora = timezone.localtime()
        prefijo = f"REC-{ahora.strftime('%Y%m%d')}-"
        ultima = Recepcion.objects.filter(
            numero_recepcion__startswith=prefijo
        ).order_by('-numero_recepcion').first()
        if ultima:
            correlativo = int(ultima.numero_recepcion.split('-')[-1]) + 1
        else:
            correlativo = 1
        return f"{prefijo}{correlativo:04d}"

    # ========== CREAR ==========
    @staticmethod
    def crear_recepcion(data):
        try:
            data = data.copy()

            if data.get('producto'):
                producto = Producto.objects.get(id=data['producto'], activo=True)
                data['producto'] = producto
            if data.get('proveedor'):
                proveedor = Proveedor.objects.get(id=data['proveedor'], activo=True)
                data['proveedor'] = proveedor

            data['numero_recepcion'] = RecepcionService.generar_numero_recepcion()
            recepcion = Recepcion(**data)
            recepcion.full_clean()
            recepcion.save()
            return recepcion

        except Producto.DoesNotExist:
            raise ValueError(f"Producto con ID {data.get('producto')} no encontrado")
        except Proveedor.DoesNotExist:
            raise ValueError(f"Proveedor con ID {data.get('proveedor')} no encontrado")
        except Exception as e:
            raise ValueError(f"Error al crear recepción: {str(e)}")

    # ========== LEER ==========
    @staticmethod
    def listar_recepciones(filtros=None):
        queryset = Recepcion.objects.all()

        if filtros:
            if filtros.get('estado'):
                queryset = queryset.filter(estado=filtros['estado'])
            if filtros.get('producto_id'):
                queryset = queryset.filter(producto_id=filtros['producto_id'])
            if filtros.get('proveedor_id'):
                queryset = queryset.filter(proveedor_id=filtros['proveedor_id'])
            if filtros.get('orden_compra'):
                queryset = queryset.filter(orden_compra__icontains=filtros['orden_compra'])
            if filtros.get('desde'):
                queryset = queryset.filter(fecha_recepcion__gte=filtros['desde'])
            if filtros.get('hasta'):
                queryset = queryset.filter(fecha_recepcion__lte=filtros['hasta'])

        return queryset

    @staticmethod
    def obtener_recepcion_por_id(recepcion_id):
        try:
            return Recepcion.objects.get(id=recepcion_id)
        except Recepcion.DoesNotExist:
            return None

    # ========== ACTUALIZAR ==========
    @staticmethod
    def actualizar_recepcion(recepcion_id, data):
        try:
            recepcion = Recepcion.objects.get(id=recepcion_id)

            if recepcion.estado not in ['PENDIENTE', 'EN_VERIFICACION']:
                raise ValueError(
                    f"No se puede modificar una recepción en estado {recepcion.estado}"
                )

            if data.get('producto'):
                producto = Producto.objects.get(id=data['producto'], activo=True)
                data['producto'] = producto
            if data.get('proveedor'):
                proveedor = Proveedor.objects.get(id=data['proveedor'], activo=True)
                data['proveedor'] = proveedor

            for key, value in data.items():
                setattr(recepcion, key, value)

            recepcion.full_clean()
            recepcion.save()
            return recepcion

        except Recepcion.DoesNotExist:
            raise ValueError(f"Recepción con ID {recepcion_id} no encontrada")
        except Producto.DoesNotExist:
            raise ValueError(f"Producto con ID {data.get('producto')} no encontrado")
        except Proveedor.DoesNotExist:
            raise ValueError(f"Proveedor con ID {data.get('proveedor')} no encontrado")
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Error al actualizar recepción: {str(e)}")

    # ========== VERIFICAR ==========
    @staticmethod
    @transaction.atomic
    def verificar_recepcion(recepcion_id, data, usuario):
        try:
            recepcion = Recepcion.objects.get(id=recepcion_id)

            if recepcion.estado not in ['PENDIENTE', 'EN_VERIFICACION']:
                raise ValueError(
                    f"No se puede verificar una recepción en estado {recepcion.estado}"
                )

            cantidad_verificada = int(data.get('cantidad_verificada', 0))
            cantidad_conforme = int(data.get('cantidad_conforme', 0))
            cantidad_no_conforme = int(data.get('cantidad_no_conforme', 0))

            if cantidad_verificada <= 0:
                raise ValueError("La cantidad verificada debe ser mayor a cero")
            if cantidad_verificada > recepcion.cantidad_recibida:
                raise ValueError(
                    f"La cantidad verificada ({cantidad_verificada}) no puede superar "
                    f"la cantidad recibida ({recepcion.cantidad_recibida})"
                )
            if cantidad_conforme + cantidad_no_conforme != cantidad_verificada:
                raise ValueError(
                    "La suma de conforme y no conforme debe igualar la cantidad verificada"
                )

            recepcion.cantidad_verificada = cantidad_verificada
            recepcion.cantidad_conforme = cantidad_conforme
            recepcion.cantidad_no_conforme = cantidad_no_conforme
            recepcion.fecha_verificacion = timezone.now()
            recepcion.verificado_por = usuario

            if cantidad_no_conforme == 0:
                recepcion.estado = 'VERIFICADA'
                recepcion.conformidad = True
            else:
                recepcion.estado = 'PARCIAL'
                recepcion.conformidad = False

            recepcion.save()
            return recepcion

        except Recepcion.DoesNotExist:
            raise ValueError(f"Recepción con ID {recepcion_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Error al verificar recepción: {str(e)}")

    # ========== CONFIRMAR ==========
    @staticmethod
    @transaction.atomic
    def confirmar_recepcion(recepcion_id, usuario):
        try:
            recepcion = Recepcion.objects.get(id=recepcion_id)

            if recepcion.estado not in ['VERIFICADA', 'PARCIAL']:
                raise ValueError(
                    f"No se puede confirmar una recepción en estado {recepcion.estado}"
                )

            producto = Producto.objects.get(id=recepcion.producto_id)
            producto.incrementar_stock(recepcion.cantidad_conforme)

            recepcion.estado = 'CONFIRMADA'
            recepcion.conformidad = True
            recepcion.fecha_confirmacion = timezone.now()
            recepcion.confirmado_por = usuario
            recepcion.save()

            return recepcion

        except Recepcion.DoesNotExist:
            raise ValueError(f"Recepción con ID {recepcion_id} no encontrada")
        except Producto.DoesNotExist:
            raise ValueError(
                "Producto asociado a la recepción no encontrado"  
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Error al confirmar recepción: {str(e)}")

    # ========== RECHAZAR ==========
    @staticmethod
    @transaction.atomic
    def rechazar_recepcion(recepcion_id, usuario, observaciones=""):
        try:
            recepcion = Recepcion.objects.get(id=recepcion_id)

            if recepcion.estado in ['CONFIRMADA', 'RECHAZADA']:
                raise ValueError(
                    f"No se puede rechazar una recepción en estado {recepcion.estado}"
                )

            recepcion.estado = 'RECHAZADA'
            recepcion.conformidad = False
            recepcion.verificado_por = usuario
            if observaciones:
                recepcion.observaciones = observaciones
            recepcion.save()

            return recepcion

        except Recepcion.DoesNotExist:
            raise ValueError(f"Recepción con ID {recepcion_id} no encontrada")
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Error al rechazar recepción: {str(e)}")

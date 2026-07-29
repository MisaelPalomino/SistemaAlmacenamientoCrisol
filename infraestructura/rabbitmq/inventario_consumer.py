import json
import logging
import os

import django
import pika


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "almacen_inventario.settings",
)
django.setup()

from django.conf import settings

from aplicacion.services.producto_service import ProductoService


LOGGER = logging.getLogger(__name__)

REQUEST_QUEUE = "crisol.inventario.request"
RESPONSE_QUEUE = "crisol.inventario.response"
MESSAGE_TYPE = "inventario.stock_bajo.consultar"
RESPONSE_TYPE = "inventario.stock_bajo.respuesta"


def crear_conexion():
    """Crea una conexión con RabbitMQ usando la configuración de Django."""
    configuracion = settings.RABBITMQ
    credenciales = pika.PlainCredentials(
        configuracion["USER"],
        configuracion["PASSWORD"],
    )

    parametros = pika.ConnectionParameters(
        host=configuracion["HOST"],
        port=configuracion["PORT"],
        virtual_host=configuracion["VIRTUAL_HOST"],
        credentials=credenciales,
        heartbeat=60,
        blocked_connection_timeout=30,
    )

    return pika.BlockingConnection(parametros)


def publicar_respuesta(channel, properties, resultado):
    """Publica el resultado de la consulta en la cola de respuestas."""
    respuesta = {
        "tipo": RESPONSE_TYPE,
        "datos": resultado,
    }

    channel.basic_publish(
        exchange="",
        routing_key=RESPONSE_QUEUE,
        body=json.dumps(respuesta, ensure_ascii=False).encode("utf-8"),
        properties=pika.BasicProperties(
            content_type="application/json",
            content_encoding="utf-8",
            delivery_mode=2,
            correlation_id=getattr(properties, "correlation_id", None),
        ),
    )


def procesar_mensaje(channel, method, properties, body):
    """Procesa una solicitud de consulta de productos con stock bajo."""
    try:
        mensaje = json.loads(body.decode("utf-8"))

        if not isinstance(mensaje, dict):
            raise ValueError("El cuerpo del mensaje debe ser un objeto JSON")

        if mensaje.get("tipo") != MESSAGE_TYPE:
            raise ValueError(
                f"Tipo de mensaje no soportado: {mensaje.get('tipo')}"
            )

        resultado = ProductoService.generar_alerta_stock_bajo()
        publicar_respuesta(channel, properties, resultado)

        channel.basic_ack(delivery_tag=method.delivery_tag)
        LOGGER.info(
            "Consulta de stock bajo procesada. correlation_id=%s",
            getattr(properties, "correlation_id", None),
        )

    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        LOGGER.warning("Mensaje de inventario inválido: %s", error)
        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False,
        )

    except Exception:
        LOGGER.exception("Error inesperado procesando el mensaje de inventario")
        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False,
        )


def iniciar_consumidor():
    """Declara las colas y comienza a consumir solicitudes de inventario."""
    conexion = None

    try:
        conexion = crear_conexion()
        channel = conexion.channel()

        channel.queue_declare(
            queue=REQUEST_QUEUE,
            durable=True,
        )
        channel.queue_declare(
            queue=RESPONSE_QUEUE,
            durable=True,
        )
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=REQUEST_QUEUE,
            on_message_callback=procesar_mensaje,
            auto_ack=False,
        )

        LOGGER.info("Esperando mensajes en la cola %s", REQUEST_QUEUE)
        channel.start_consuming()

    except KeyboardInterrupt:
        LOGGER.info("Consumidor detenido por el usuario")

    except pika.exceptions.AMQPError:
        LOGGER.exception("No se pudo establecer o mantener la conexión con RabbitMQ")
        raise

    finally:
        if conexion is not None and conexion.is_open:
            conexion.close()
            LOGGER.info("Conexión con RabbitMQ cerrada")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    iniciar_consumidor()

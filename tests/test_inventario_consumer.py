import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from infraestructura.rabbitmq import inventario_consumer


def crear_metadatos(delivery_tag=10, correlation_id="consulta-123"):
    method = SimpleNamespace(delivery_tag=delivery_tag)
    properties = SimpleNamespace(correlation_id=correlation_id)
    return method, properties


def test_procesa_mensaje_valido():
    channel = Mock()
    method, properties = crear_metadatos()
    body = json.dumps(
        {"tipo": inventario_consumer.MESSAGE_TYPE}
    ).encode("utf-8")
    resultado = {"alerta": False, "total": 0}

    with (
        patch.object(
            inventario_consumer.ProductoService,
            "generar_alerta_stock_bajo",
            return_value=resultado,
        ) as generar_alerta,
        patch.object(inventario_consumer, "publicar_respuesta") as publicar,
    ):
        inventario_consumer.procesar_mensaje(
            channel,
            method,
            properties,
            body,
        )

    generar_alerta.assert_called_once_with()
    publicar.assert_called_once_with(channel, properties, resultado)
    channel.basic_nack.assert_not_called()


def test_publica_respuesta_correcta():
    channel = Mock()
    _, properties = crear_metadatos(correlation_id="consulta-456")
    resultado = {
        "alerta": True,
        "total": 1,
        "productos": [{"id": 1, "nombre": "El Principito"}],
    }

    inventario_consumer.publicar_respuesta(
        channel,
        properties,
        resultado,
    )

    channel.basic_publish.assert_called_once()
    argumentos = channel.basic_publish.call_args.kwargs
    respuesta = json.loads(argumentos["body"].decode("utf-8"))

    assert argumentos["exchange"] == ""
    assert argumentos["routing_key"] == inventario_consumer.RESPONSE_QUEUE
    assert respuesta == {
        "tipo": inventario_consumer.RESPONSE_TYPE,
        "datos": resultado,
    }
    assert argumentos["properties"].content_type == "application/json"
    assert argumentos["properties"].content_encoding == "utf-8"
    assert argumentos["properties"].delivery_mode == 2
    assert argumentos["properties"].correlation_id == "consulta-456"


def test_confirma_mensaje_valido_con_ack():
    channel = Mock()
    method, properties = crear_metadatos(delivery_tag=25)
    body = json.dumps(
        {"tipo": inventario_consumer.MESSAGE_TYPE}
    ).encode("utf-8")

    with (
        patch.object(
            inventario_consumer.ProductoService,
            "generar_alerta_stock_bajo",
            return_value={"alerta": False, "total": 0},
        ),
        patch.object(inventario_consumer, "publicar_respuesta"),
    ):
        inventario_consumer.procesar_mensaje(
            channel,
            method,
            properties,
            body,
        )

    channel.basic_ack.assert_called_once_with(delivery_tag=25)
    channel.basic_nack.assert_not_called()


def test_rechaza_json_invalido_con_nack():
    channel = Mock()
    method, properties = crear_metadatos(delivery_tag=30)
    body = b'{"tipo": "mensaje-incompleto"'

    with patch.object(
        inventario_consumer.ProductoService,
        "generar_alerta_stock_bajo",
    ) as generar_alerta:
        inventario_consumer.procesar_mensaje(
            channel,
            method,
            properties,
            body,
        )

    generar_alerta.assert_not_called()
    channel.basic_publish.assert_not_called()
    channel.basic_ack.assert_not_called()
    channel.basic_nack.assert_called_once_with(
        delivery_tag=30,
        requeue=False,
    )


def test_rechaza_tipo_de_mensaje_desconocido_con_nack():
    channel = Mock()
    method, properties = crear_metadatos(delivery_tag=40)
    body = json.dumps(
        {"tipo": "inventario.mensaje.desconocido"}
    ).encode("utf-8")

    with patch.object(
        inventario_consumer.ProductoService,
        "generar_alerta_stock_bajo",
    ) as generar_alerta:
        inventario_consumer.procesar_mensaje(
            channel,
            method,
            properties,
            body,
        )

    generar_alerta.assert_not_called()
    channel.basic_publish.assert_not_called()
    channel.basic_ack.assert_not_called()
    channel.basic_nack.assert_called_once_with(
        delivery_tag=40,
        requeue=False,
    )

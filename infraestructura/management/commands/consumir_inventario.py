from django.core.management.base import BaseCommand, CommandError
from pika.exceptions import AMQPError

from infraestructura.rabbitmq.inventario_consumer import iniciar_consumidor


class Command(BaseCommand):
    help = "Inicia el consumidor RabbitMQ de consultas de inventario"

    def handle(self, *args, **options):
        try:
            iniciar_consumidor()
        except AMQPError as error:
            raise CommandError(
                f"No se pudo conectar con RabbitMQ: {error}"
            ) from error

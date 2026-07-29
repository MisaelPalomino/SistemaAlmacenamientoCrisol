from django.core.management.base import BaseCommand, CommandError
from pika.exceptions import AMQPError

from infraestructura.rabbitmq.inventario_consumer import iniciar_consumidor


class Command(BaseCommand):
    help = "Inicia el consumidor RabbitMQ de consultas de inventario"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Esperando mensajes en la cola crisol.inventario.request..."
            )
        )

        try:
            iniciar_consumidor()
        except AMQPError as error:
            raise CommandError(
                f"No se pudo conectar con RabbitMQ: {error}"
            ) from error

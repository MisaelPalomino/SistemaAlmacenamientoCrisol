from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from .producto import Producto
from .recepcion import Recepcion


class Incidencia(models.Model):
    """
    Entidad Incidencia - Representa cualquier incidencia en el inventario
    """

    TIPOS = [
        ("PRODUCTO_DETERIORADO", "Producto Deteriorado"),
        ("PRODUCTO_FALTANTE", "Producto Faltante"),
        ("PRODUCTO_SOBRANTE", "Producto Sobrante"),
        ("PRODUCTO_DAÑADO", "Producto Dañado"),
        ("DEVOLUCION", "Devolución"),
        ("PERDIDA", "Pérdida"),
        ("ROTURA", "Rotura"),
        ("CADUCIDAD", "Producto Caducado"),
        ("OTRO", "Otro"),
    ]

    PRIORIDADES = [
        ("BAJA", "Baja"),
        ("MEDIA", "Media"),
        ("ALTA", "Alta"),
        ("CRITICA", "Crítica"),
    ]

    ESTADOS = [
        ("REGISTRADA", "Registrada"),
        ("EN_REVISION", "En Revisión"),
        ("EN_PROCESO", "En Proceso de Resolución"),
        ("RESUELTA", "Resuelta"),
        ("CERRADA", "Cerrada"),
    ]

    # ========== IDENTIFICACIÓN ==========
    codigo_incidencia = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Formato: INC-YYYY-MMDD-XXX",
    )

    # ========== RELACIONES ==========
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="incidencias"
    )
    recepcion = models.ForeignKey(
        Recepcion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidencias",
    )

    # ========== DATOS DE LA INCIDENCIA ==========
    tipo = models.CharField(max_length=30, choices=TIPOS)
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default="MEDIA")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="REGISTRADA")
    descripcion = models.TextField()
    cantidad_afectada = models.PositiveIntegerField()
    impacto_economico = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Impacto económico estimado en soles",
    )

    # ========== FECHAS ==========
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    # ========== RESPONSABLES ==========
    responsable = models.CharField(
        max_length=100, help_text="Persona que reporta la incidencia"
    )
    asignado_a = models.CharField(
        max_length=100, blank=True, help_text="Persona asignada para resolver"
    )

    # ========== SOLUCIÓN ==========
    observaciones = models.TextField(blank=True)
    solucion_aplicada = models.TextField(blank=True)
    accion_correctiva = models.TextField(blank=True)

    class Meta:
        db_table = "incidencias"
        ordering = ["-fecha_registro"]
        verbose_name = "Incidencia"
        verbose_name_plural = "Incidencias"

    def __str__(self):
        return f"Incidencia {self.codigo_incidencia} - {self.tipo}"

    def clean(self):
        if self.cantidad_afectada <= 0:
            raise ValidationError("La cantidad afectada debe ser positiva")
        if self.impacto_economico < 0:
            raise ValidationError("El impacto económico no puede ser negativo")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    # ========== MÉTODOS DE NEGOCIO ==========
    def asignar(self, asignado_a: str):
        if self.estado != "REGISTRADA":
            raise ValueError("Solo se pueden asignar incidencias en estado REGISTRADA")
        self.asignado_a = asignado_a
        self.estado = "EN_REVISION"
        self.fecha_asignacion = timezone.now()
        self.save()

    def resolver(self, solucion: str):
        if self.estado not in ["EN_REVISION", "EN_PROCESO"]:
            raise ValueError(
                "Solo se pueden resolver incidencias en proceso o revisión"
            )
        self.solucion_aplicada = solucion
        self.estado = "RESUELTA"
        self.fecha_resolucion = timezone.now()
        self.save()

    def cerrar(self):
        if self.estado != "RESUELTA":
            raise ValueError("Solo se pueden cerrar incidencias resueltas")
        self.estado = "CERRADA"
        self.fecha_cierre = timezone.now()
        self.save()

    def clasificar(self, nueva_prioridad: str):
        if nueva_prioridad not in ["BAJA", "MEDIA", "ALTA", "CRITICA"]:
            raise ValueError("Prioridad inválida")
        self.prioridad = nueva_prioridad
        self.save()

    @property
    def es_critica(self):
        return self.prioridad == "CRITICA"

    @property
    def esta_activa(self):
        return self.estado != "CERRADA"
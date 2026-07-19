from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from .producto import Producto

class SolicitudReposicion(models.Model):
    """
    Entidad Solicitud de Reposición - Para reponer stock de productos
    """
    
    ESTADOS = [
        ('CREADA', 'Creada'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADA', 'Aprobada'),
        ('EN_EJECUCION', 'En Ejecución'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    PRIORIDADES = [
        ('NORMAL', 'Normal'),
        ('URGENTE', 'Urgente'),
        ('CRITICA', 'Crítica'),
    ]
    
    # ========== IDENTIFICACIÓN ==========
    numero_solicitud = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Formato: REP-YYYY-MMDD-XXX"
    )
    
    # ========== RELACIONES ==========
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='solicitudes_reposicion'
    )
    
    # ========== CANTIDADES ==========
    cantidad_solicitada = models.PositiveIntegerField()
    cantidad_aprobada = models.PositiveIntegerField(default=0)
    cantidad_repuesta = models.PositiveIntegerField(default=0)
    
    # ========== FECHAS ==========
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_ejecucion = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    # ========== ESTADO ==========
    estado = models.CharField(max_length=20, choices=ESTADOS, default='CREADA')
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='NORMAL')
    motivo = models.TextField()
    
    # ========== RESPONSABLES ==========
    aprobado_por = models.CharField(max_length=100, blank=True)
    ejecutado_por = models.CharField(max_length=100, blank=True)
    
    # ========== INFORMACIÓN ADICIONAL ==========
    observaciones = models.TextField(blank=True)
    proveedor = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'solicitudes_reposicion'
        ordering = ['-fecha_solicitud']
        verbose_name = 'Solicitud de Reposición'
        verbose_name_plural = 'Solicitudes de Reposición'
    
    def __str__(self):
        return f"Solicitud {self.numero_solicitud} - {self.producto.nombre}"
    
    def clean(self):
        if self.cantidad_solicitada <= 0:
            raise ValidationError("La cantidad solicitada debe ser positiva")
        if self.cantidad_aprobada > self.cantidad_solicitada:
            raise ValidationError("La cantidad aprobada no puede exceder la solicitada")
        if self.cantidad_repuesta > self.cantidad_aprobada:
            raise ValidationError("La cantidad repuesta no puede exceder la aprobada")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    # ========== MÉTODOS DE NEGOCIO ==========
    def aprobar(self, aprobado_por: str, cantidad_aprobada: int = None):
        if self.estado not in ['CREADA', 'EN_REVISION']:
            raise ValueError("Solo se pueden aprobar solicitudes en estado CREADA o EN_REVISION")
        
        cantidad = cantidad_aprobada if cantidad_aprobada else self.cantidad_solicitada
        
        if cantidad <= 0:
            raise ValueError("La cantidad aprobada debe ser positiva")
        if cantidad > self.cantidad_solicitada:
            raise ValueError(f"La cantidad aprobada ({cantidad}) excede la solicitada ({self.cantidad_solicitada})")
        
        self.cantidad_aprobada = cantidad
        self.aprobado_por = aprobado_por
        self.estado = 'APROBADA'
        self.fecha_aprobacion = timezone.now()
        self.save()
    
    def completar(self, cantidad_repuesta: int):
        if self.estado != 'EN_EJECUCION':
            raise ValueError("Solo se pueden completar solicitudes en ejecución")
        if cantidad_repuesta <= 0:
            raise ValueError("La cantidad repuesta debe ser positiva")
        if cantidad_repuesta > self.cantidad_aprobada:
            raise ValueError(f"La cantidad repuesta ({cantidad_repuesta}) excede la aprobada ({self.cantidad_aprobada})")
        
        self.cantidad_repuesta = cantidad_repuesta
        self.estado = 'COMPLETADA'
        self.fecha_completada = timezone.now()
        self.save()
        
        # Actualizar stock
        self.producto.incrementar_stock(cantidad_repuesta)
    
    def cancelar(self, motivo: str):
        if self.estado in ['COMPLETADA', 'CANCELADA']:
            raise ValueError("No se puede cancelar una solicitud completada o ya cancelada")
        self.estado = 'CANCELADA'
        self.observaciones = f"CANCELADA: {motivo}"
        self.save()
    
    @property
    def esta_activa(self):
        return self.estado in ['CREADA', 'EN_REVISION', 'APROBADA', 'EN_EJECUCION']
    
    @property
    def porcentaje_ejecutado(self):
        if self.cantidad_aprobada == 0:
            return 0.0
        return (self.cantidad_repuesta / self.cantidad_aprobada) * 100
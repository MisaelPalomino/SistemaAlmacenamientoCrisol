from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from .producto import Producto
from .proveedor import Proveedor

class Recepcion(models.Model):
    """Modelo Recepción - Librerías Crisol"""
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_VERIFICACION', 'En Verificación'),
        ('VERIFICADA', 'Verificada'),
        ('CONFIRMADA', 'Confirmada'),
        ('PARCIAL', 'Parcial'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    numero_recepcion = models.CharField(max_length=50, unique=True, db_index=True)
    orden_compra = models.CharField(max_length=50, db_index=True)
    
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='recepciones')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='recepciones')
    
    cantidad_esperada = models.PositiveIntegerField()
    cantidad_recibida = models.PositiveIntegerField(default=0)
    cantidad_verificada = models.PositiveIntegerField(default=0)
    cantidad_conforme = models.PositiveIntegerField(default=0)
    cantidad_no_conforme = models.PositiveIntegerField(default=0)
    
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    fecha_esperada_entrega = models.DateField()
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    conformidad = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    
    creado_por = models.CharField(max_length=100)
    verificado_por = models.CharField(max_length=100, blank=True)
    confirmado_por = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'recepciones'
        ordering = ['-fecha_recepcion']
    
    def __str__(self):
        return f"Recepción {self.numero_recepcion} - {self.producto.nombre}"
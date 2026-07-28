from django.db import models
from django.core.exceptions import ValidationError

class Proveedor(models.Model):
    """Modelo Proveedor - Librerías Crisol"""
    
    CALIFICACION_CHOICES = [
        ('A', 'Excelente'),
        ('B', 'Bueno'),
        ('C', 'Regular'),
        ('D', 'Malo'),
    ]
    
    ruc = models.CharField(max_length=11, unique=True, db_index=True)
    razon_social = models.CharField(max_length=200)
    nombre_comercial = models.CharField(max_length=200)
    
    direccion_calle = models.CharField(max_length=200)
    direccion_numero = models.CharField(max_length=20)
    direccion_distrito = models.CharField(max_length=100)
    direccion_provincia = models.CharField(max_length=100)
    direccion_departamento = models.CharField(max_length=100)
    direccion_codigo_postal = models.CharField(max_length=10, blank=True)
    direccion_referencia = models.TextField(blank=True)
    
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    telefono_alternativo = models.CharField(max_length=20, blank=True)
    
    especialidad = models.CharField(max_length=100)
    plazo_entrega_dias = models.PositiveIntegerField()
    condiciones_pago = models.CharField(max_length=100)
    calificacion = models.CharField(max_length=1, choices=CALIFICACION_CHOICES, default='B')
    es_nacional = models.BooleanField(default=True)
    
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'proveedores'
        ordering = ['razon_social']
    
    def __str__(self):
        return f"{self.razon_social} ({self.ruc})"
    
    def clean(self):
        if not self.ruc or len(self.ruc) != 11:
            raise ValidationError("RUC debe tener 11 dígitos")
        if self.plazo_entrega_dias <= 0:
            raise ValidationError("El plazo de entrega debe ser positivo")
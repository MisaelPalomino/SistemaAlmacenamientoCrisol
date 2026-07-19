from django.db import models
from django.core.exceptions import ValidationError

class Almacen(models.Model):
    """
    Entidad Almacén - Representa tiendas físicas y almacenes
    """
    
    TIPOS = [
        ('TIENDA_FISICA', 'Tienda Física'),
        ('ALMACEN_CENTRAL', 'Almacén Central'),
        ('ALMACEN_SECUNDARIO', 'Almacén Secundario'),
        ('PUNTO_VENTA', 'Punto de Venta'),
    ]
    
    # ========== IDENTIFICACIÓN ==========
    codigo_almacen = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Código único del almacén/tienda"
    )
    nombre = models.CharField(max_length=200)
    
    # ========== DIRECCIÓN ==========
    direccion_calle = models.CharField(max_length=200)
    direccion_numero = models.CharField(max_length=20)
    direccion_distrito = models.CharField(max_length=100)
    direccion_provincia = models.CharField(max_length=100)
    direccion_departamento = models.CharField(max_length=100)
    direccion_codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    direccion_referencia = models.TextField(blank=True, null=True)
    
    # ========== CONTACTO ==========
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    telefono_alternativo = models.CharField(max_length=20, blank=True)
    
    # ========== DATOS DEL ALMACÉN ==========
    tipo = models.CharField(max_length=20, choices=TIPOS)
    capacidad_maxima = models.PositiveIntegerField(help_text="Capacidad máxima en unidades")
    capacidad_actual = models.PositiveIntegerField(default=0, help_text="Capacidad actual ocupada")
    
    # ========== HORARIO ==========
    horario_apertura = models.CharField(max_length=10, default="09:00")
    horario_cierre = models.CharField(max_length=10, default="21:00")
    dias_atencion = models.CharField(max_length=100, default="Lun-Sab")
    
    # ========== DATOS DE GESTIÓN ==========
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'almacenes'
        ordering = ['nombre']
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo_almacen})"
    
    def clean(self):
        if self.capacidad_maxima <= 0:
            raise ValidationError("La capacidad máxima debe ser positiva")
        if self.capacidad_actual < 0:
            raise ValidationError("La capacidad actual no puede ser negativa")
        if self.capacidad_actual > self.capacidad_maxima:
            raise ValidationError("La capacidad actual no puede exceder la máxima")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    # ========== MÉTODOS DE NEGOCIO ==========
    def aumentar_ocupacion(self, cantidad: int):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")
        nueva_capacidad = self.capacidad_actual + cantidad
        if nueva_capacidad > self.capacidad_maxima:
            raise ValueError(f"Capacidad excedida. Máxima: {self.capacidad_maxima}")
        self.capacidad_actual = nueva_capacidad
        self.save()
    
    def disminuir_ocupacion(self, cantidad: int):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")
        if self.capacidad_actual < cantidad:
            raise ValueError(f"Capacidad insuficiente. Actual: {self.capacidad_actual}")
        self.capacidad_actual -= cantidad
        self.save()
    
    @property
    def capacidad_disponible(self):
        return self.capacidad_maxima - self.capacidad_actual
    
    @property
    def porcentaje_ocupacion(self):
        if self.capacidad_maxima == 0:
            return 0.0
        return (self.capacidad_actual / self.capacidad_maxima) * 100
    
    @property
    def esta_lleno(self):
        return self.capacidad_actual >= self.capacidad_maxima
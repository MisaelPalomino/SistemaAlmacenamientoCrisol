from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

class Producto(models.Model):
    """Modelo Producto - Librerías Crisol"""
    
    TIPO_PRODUCTO = [
        ('LIBRO', 'Libro'),
        ('REVISTA', 'Revista'),
        ('PAPELERIA', 'Papelería'),
        ('ENTRETENIMIENTO', 'Entretenimiento'),
        ('OTRO', 'Otro'),
    ]
    
    CATEGORIAS = [
        ('LITERATURA', 'Literatura'),
        ('CIENCIA', 'Ciencia'),
        ('EDUCACION', 'Educación'),
        ('INFANTIL', 'Infantil'),
        ('OFICINA', 'Oficina'),
        ('ESCOLAR', 'Escolar'),
        ('OTRO', 'Otro'),
    ]
    
    isbn = models.CharField(max_length=20, unique=True, db_index=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_PRODUCTO, default='LIBRO')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    
    editorial = models.CharField(max_length=100, blank=True)
    autor = models.CharField(max_length=200, blank=True)
    año_publicacion = models.IntegerField(null=True, blank=True)
    
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    
    stock_minimo = models.PositiveIntegerField(default=5)
    stock_maximo = models.PositiveIntegerField(default=50)
    stock_actual = models.PositiveIntegerField(default=0)
    ubicacion = models.CharField(max_length=100, blank=True)
    pasillo = models.CharField(max_length=10, blank=True)
    estante = models.CharField(max_length=10, blank=True)
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    proveedor_principal = models.ForeignKey(
        'Proveedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos'
    )
    
    class Meta:
        db_table = 'productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.isbn})"
    
    def clean(self):
        if self.precio_compra <= 0:
            raise ValidationError("El precio de compra debe ser positivo")
        if self.precio_venta <= 0:
            raise ValidationError("El precio de venta debe ser positivo")
        if self.precio_venta <= self.precio_compra:
            raise ValidationError("El precio de venta debe ser mayor al precio de compra")
        if self.stock_maximo < self.stock_minimo:
            raise ValidationError("El stock máximo debe ser mayor al stock mínimo")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def incrementar_stock(self, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")
        self.stock_actual += cantidad
        self.save()
    
    @property
    def tiene_stock_bajo(self):
        return self.stock_actual <= self.stock_minimo
    
    @property
    def valor_inventario(self):
        return self.stock_actual * self.precio_compra
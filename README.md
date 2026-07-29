# Sistema de Almacenamiento - Librerías Crisol

Proyecto Django con arquitectura en capas (DDD) para la gestión de inventario de Librerías Crisol.

## Arquitectura

| Capa             | App               | Propósito                         |
|------------------|-------------------|-----------------------------------|
| Dominio          | `dominio`         | Modelos de datos (entidades)      |
| Aplicación       | `aplicacion`      | Servicios con lógica de negocio   |
| Presentación     | `presentacion`    | API REST (views, serializers)     |
| Infraestructura  | `infraestructura` | Integraciones externas            |

### Visión de la Arquitectura

El Sistema de Almacenamiento Crisol está diseñado con una arquitectura en capas basada en DDD (Domain-Driven Design), implementada sobre Django REST Framework. 
Esta arquitectura refleja los procesos de negocio documentados en el análisis BPMN de Librerías Crisol S.A.C., abarcando la Gestión de Abastecimiento, Gestión de 
Inventario, Ventas en Tienda, Atención al Cliente, Marketing y Promoción, y Gestión de Pedidos Online.

Una característica fundamental de esta arquitectura es la ausencia de repositorios (repos), reemplazándolos directamente con el ORM de Django como capa de acceso 
a datos dentro de la infraestructura.

### Mapeo de Capas DDD con Procesos de Negocio Crisol

| Capa DDD	         | App/Componente	               | Propósito	                                       | Procesos Crisol Soportados                                           |
|--------------------|--------------------------------|--------------------------------------------------|----------------------------------------------------------------------|
| Dominio	         | dominio/models/	               | Entidades, Value Objects, Agregados	            | Abastecimiento, Inventario, Ventas, Atención, Marketing, E-commerce  |
| Aplicación	      | aplicacion/services/	         | Casos de uso, lógica orquestadora	               | Orquestación de procesos BPMN                                        |
| Presentación	      | presentacion/	               | API REST, DTOs (Serializers)	                  | Interfaces para tienda física, web y móvil                           | 
| Infraestructura	   | Django ORM + Integraciones	   | Persistencia, APIs externas, notificaciones	   | SUNAT, pasarelas de pago, couriers, CRM                              | 

### Principios Arquitectónicos

No Uso de Repositorios (Repository Pattern)
Decisión estratégica: En lugar de implementar un patrón repositorio, utilizamos directamente el ORM de Django como la capa de infraestructura para todas las operaciones 
de persistencia.

#### ¿Por qué?

- El ORM de Django ya proporciona una abstracción suficientemente robusta y expresiva
- La capa de infraestructura es transparente al dominio
- Los servicios de aplicación pueden acceder directamente a Model.objects.*
- Django ORM incluye características avanzadas (lazy loading, transacciones, migraciones)
- Alineado con el análisis BPMN: Las entidades definidas en los modelos de datos de Bonita se mapean directamente a modelos Django

#### Beneficios en el contexto Crisol:

- Menor código boilerplate y menos archivos
- Mayor simplicidad en el mantenimiento
- Aprovechamiento completo de las características nativas de Django
- Curva de aprendizaje más baja para nuevos desarrolladores
- Se mantiene la separación de capas sin añadir complejidad artificial
- Las reglas de negocio (stock mínimo, validaciones de ISBN, políticas de cambio) se implementan directamente en los modelos

#### Caso concreto: Proceso de Venta en Tienda

1. Cliente solicita libro (presentacion/views/venta_views.py)
2. Asesor consulta stock vía API (presentacion/serializers/)
3. Servicio valida disponibilidad (aplicacion/services/venta_service.py)
4. ORM consulta Producto.objects.filter(isbn=...)
5. Si hay stock, procesa pago (infraestructura/integraciones/pasarela_pago.py)
6. ORM actualiza stock: Producto.objects.filter(id=...).update(stock=F('stock')-1)
7. Servicio genera factura (infraestructura/integraciones/sunat.py)
8. Notifica al cliente (infraestructura/integraciones/notificaciones.py)

#### Mapeo de Procesos BPMN a Componentes Django

| Proceso Crisol	   | Entidad BPMN	              | Modelo Django          | Servicio Aplicación	 | Integración                 | 
|--------------------|----------------------------|------------------------|------------------------|-----------------------------|
| Abastecimiento	   | OrdenCompra, Proveedor     | OrdenCompra, Proveedor | AbastecimientoService	 | Email, ERP                  | 
| Gestión Inventario |	Producto, EntradaProducto | Producto, Recepcion	   | InventarioService	    | -                           |
| Ventas Tienda      |	VentaTienda	              | Venta, Cliente	      | VentaService	          | SUNAT, Pasarela Pago        |
| Atención Cliente   |	Ticket, Cliente	        | Atencion, Ticket	      | AtencionService	       | CRM, Notificaciones         |
| Marketing	         | Campaña, Promoción	        | Campaña, Promocion	   | MarketingService	    | Email Marketing, Analytics  |
| Pedidos Online	   | Pedido, Envio, Pago	     | Pedido, Envio, Pago	   | PedidoService	       | Courier, Pasarela Pago      |

#### Ventajas en el Contexto DDD para Crisol

| Aspecto DDD	            | Implementación en Crisol	                           | Proceso de Negocio Asociado          |
|--------------------------|-----------------------------------------------------|--------------------------------------| 
| Entidades	               | Modelos Django con métodos de dominio	            | Producto, Proveedor, Cliente, Pedido |
| Value Objects	         | Campos con lógica de validación (ISBN, DNI, Email)	| Validación de RUC, DNI, emails       | 
| Agregados	               | Relaciones entre modelos gestionadas por ORM	      | Pedido → DetallePedido → Producto    | 
| Servicios de Dominio	   | Métodos en modelos para reglas específicas	         | Producto.validar_stock_minimo()      | 
| Servicios de Aplicación	| Orquestan casos de uso con transaction.atomic()	   | Procesar venta, registrar recepción  | 
| Repositorios	            | Reemplazados por QuerySets de Django	               | Todas las consultas BPMN             | 
| Eventos de Dominio	      | Signals de Django (stock bajo, pedido creado)	      | Alertas automáticas de reposición    | 

#### Gestión de Transacciones y Consistencia

Los procesos de negocio de Crisol requieren consistencia transaccional, especialmente en:

- Compra online: Validar stock → Cobrar → Actualizar inventario → Generar guía
- Venta en tienda: Verificar stock → Cobrar → Actualizar inventario → Facturar
- Recepción: Registrar ingreso → Actualizar stock → Conciliar con orden de compra

Django ORM maneja esto de forma nativa:

```bash
from django.db import transaction

@transaction.atomic
def procesar_pedido_completo(datos_pedido):
    # Todas las operaciones son atómicas
    pedido = Pedido.objects.create(...)
    for item in datos_pedido['items']:
        Producto.objects.filter(id=item.id).update(
            stock=F('stock') - item.cantidad
        )
        DetallePedido.objects.create(pedido=pedido, ...)
    Pago.objects.create(pedido=pedido, ...)
    # Si algo falla, todo se revierte
```

#### Escalabilidad y Rendimiento

A pesar de no usar repositorios, el sistema es escalable gracias a:

- QuerySets optimizados: select_related(), prefetch_related(), only(), defer()
- Transacciones explícitas: Control fino con transaction.atomic()
- Caché: Django Cache Framework para consultas frecuentes
- Índices: Definidos en modelos para consultas rápidas (ISBN, DNI, fechas)
- Lecturas replicadas: Configuración de múltiples bases de datos

## Servicios

### Servicio de Productos — Misael Palomino

CRUD completo de productos con alertas de stock, valor de inventario y filtros.

#### Endpoints

| Método | Endpoint                              | Descripción                     |
|--------|---------------------------------------|---------------------------------|
| GET    | `/api/productos/`                     | Listar productos (con filtros)  |
| POST   | `/api/productos/`                     | Crear producto                  |
| GET    | `/api/productos/{id}/`                | Obtener producto por ID         |
| PUT    | `/api/productos/{id}/`                | Actualizar producto             |
| DELETE | `/api/productos/{id}/`                | Eliminar producto (soft-delete) |
| GET    | `/api/productos/buscar/`              | Buscar por ISBN (`?isbn=xxx`)   |
| PATCH  | `/api/productos/{id}/stock/`          | Ajustar stock                   |
| PATCH  | `/api/productos/{id}/precios/`        | Actualizar precios              |
| PATCH  | `/api/productos/{id}/activar/`        | Reactivar producto              |
| GET    | `/api/productos/alertas_stock_bajo/`  | Alertas de stock bajo           |
| GET    | `/api/productos/valor_inventario/`    | Valor total del inventario      |
| GET    | `/api/productos/categoria/`           | Filtrar por categoría           |

#### Filtros (`GET /api/productos/`)

| Parámetro      | Descripción                       |
|----------------|-----------------------------------|
| `categoria`    | Filtrar por categoría             |
| `tipo`         | Filtrar por tipo                  |
| `stock_bajo`   | Solo productos con stock bajo     |
| `search`       | Búsqueda por nombre, ISBN, autor  |
| `proveedor_id` | Filtrar por proveedor             |

---

### Servicio de Recepciones — Arthur Meza

Registro y control de recepciones de productos. Flujo completo: registro → verificación → confirmación (actualiza stock automáticamente) o rechazo.

#### Endpoints

| Método | Endpoint                              | Descripción                     |
|--------|---------------------------------------|---------------------------------|
| POST   | `/api/recepciones/`                   | Registrar una recepción         |
| GET    | `/api/recepciones/`                   | Listar recepciones              |
| GET    | `/api/recepciones/{id}/`              | Obtener recepción por ID        |
| PUT    | `/api/recepciones/{id}/`              | Actualizar recepción            |
| POST   | `/api/recepciones/{id}/verificar/`    | Verificar (conforme → VERIFICADA, no conforme → PARCIAL) |
| POST   | `/api/recepciones/{id}/confirmar/`    | Confirmar (actualiza stock automáticamente)             |
| POST   | `/api/recepciones/{id}/rechazar/`     | Rechazar recepción              |

#### Filtros (`GET /api/recepciones/`)

| Parámetro      | Descripción                          |
|----------------|--------------------------------------|
| `estado`       | Filtrar por estado                   |
| `producto_id`  | Filtrar por producto                 |
| `proveedor_id` | Filtrar por proveedor                |
| `orden_compra` | Filtrar por orden de compra          |
| `desde`        | Fecha inicial (YYYY-MM-DD)           |
| `hasta`        | Fecha final (YYYY-MM-DD)             |
| `vista=simple` | Respuesta simplificada               |

#### Flujo de estados

```
PENDIENTE ──→ VERIFICADA ──→ CONFIRMADA
    │                         (↑ stock)
    ├──→ PARCIAL ───→ CONFIRMADA
    │                  (↑ stock)
    └──→ RECHAZADA
```

| Estado             | Descripción                                    |
|--------------------|------------------------------------------------|
| `PENDIENTE`        | Recién registrada, pendiente de verificación   |
| `VERIFICADA`       | Verificada, todo conforme                      |
| `PARCIAL`          | Verificada con algunas unidades no conformes   |
| `CONFIRMADA`       | Confirmada, stock del producto actualizado     |
| `RECHAZADA`        | Rechazada                                      |

## Estructura del Proyecto

```
📦 SistemaAlmacenamientoCrisol/
├── 📁 almacen_inventario/           # Configuración Django
│   ├── settings.py
│   └── urls.py
├── 📁 dominio/models/               # Modelos (entidades)
│   ├── producto.py
│   ├── proveedor.py
│   ├── recepcion.py
│   ├── incidencia.py
│   ├── reposicion.py
│   └── almacen.py
├── 📁 aplicacion/services/          # Lógica de negocio
│   ├── producto_service.py
│   └── recepcion_service.py
├── 📁 presentacion/
│   ├── 📁 views/
│   │   ├── producto_views.py
│   │   └── recepcion_views.py
│   ├── 📁 serializers/
│   │   ├── producto_serializer.py
│   │   └── recepcion_serializer.py
│   └── 📁 urls/
│       ├── producto_urls.py
│       └── recepcion_urls.py
├── 📁 tests/
│   └── test_recepcion_api.py        # Pruebas (5 casos BDD)
├── manage.py
└── requirements.txt
```

## Instalación

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Ejecutar Pruebas

```bash
pytest tests/ -v --cov=.
```

## Ejemplos de Uso

### Productos

```bash
# Crear producto
curl -X POST http://localhost:8000/api/productos/ \
  -H "Content-Type: application/json" \
  -d '{
    "isbn": "9786120012345",
    "nombre": "El Principito",
    "tipo": "LIBRO",
    "categoria": "LITERATURA",
    "precio_compra": 25.00,
    "precio_venta": 45.00,
    "stock_actual": 10,
    "proveedor_principal": 1
  }'

# Buscar por ISBN
curl http://localhost:8000/api/productos/buscar/?isbn=9786120012345

# Alertas de stock bajo
curl http://localhost:8000/api/productos/alertas_stock_bajo/
```

### Recepciones

```bash
# 1. Registrar recepción
curl -X POST http://localhost:8000/api/recepciones/ \
  -H "Content-Type: application/json" \
  -d '{
    "orden_compra": "OC-2024-00123",
    "producto": 1,
    "proveedor": 1,
    "cantidad_esperada": 30,
    "cantidad_recibida": 30,
    "fecha_esperada_entrega": "2024-07-15",
    "creado_por": "Juan Pérez"
  }'

# 2. Verificar (conforme)
curl -X POST http://localhost:8000/api/recepciones/1/verificar/ \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad_verificada": 30,
    "cantidad_conforme": 30,
    "cantidad_no_conforme": 0,
    "verificado_por": "Carlos López"
  }'

# 3. Verificar (no conforme → parcial)
curl -X POST http://localhost:8000/api/recepciones/1/verificar/ \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad_verificada": 30,
    "cantidad_conforme": 25,
    "cantidad_no_conforme": 5,
    "verificado_por": "Carlos López"
  }'

# 4. Confirmar (actualiza stock automáticamente)
curl -X POST http://localhost:8000/api/recepciones/1/confirmar/ \
  -H "Content-Type: application/json" \
  -d '{"confirmado_por": "María García"}'

# 5. Rechazar
curl -X POST http://localhost:8000/api/recepciones/1/rechazar/ \
  -H "Content-Type: application/json" \
  -d '{
    "rechazado_por": "Admin",
    "observaciones": "Producto en mal estado"
  }'
```

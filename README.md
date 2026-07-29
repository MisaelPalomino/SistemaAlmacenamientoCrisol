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

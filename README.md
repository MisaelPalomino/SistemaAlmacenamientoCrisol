# Sistema de Almacenamiento - Librerías Crisol

Proyecto Django con arquitectura en capas (DDD) para la gestión de inventario de Librerías Crisol.

## Arquitectura

| Capa             | App               | Propósito                         |
|------------------|-------------------|-----------------------------------|
| Dominio          | `dominio`         | Modelos de datos (entidades)      |
| Aplicación       | `aplicacion`      | Servicios con lógica de negocio   |
| Presentación     | `presentacion`    | API REST (views, serializers)     |
| Infraestructura  | `infraestructura` | Integraciones externas            |

## Servicios

### Servicio de Productos — Integrante 1

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

### Servicio de Proveedores — Integrante 2

CRUD completo de proveedores con búsqueda por RUC, clasificación, filtros y desactivación lógica.

#### Endpoints

| Método | Endpoint                                      | Descripción                              |
|--------|-----------------------------------------------|------------------------------------------|
| POST   | `/api/proveedores/`                           | Crear proveedor                          |
| GET    | `/api/proveedores/`                           | Listar proveedores activos               |
| GET    | `/api/proveedores/{id}/`                      | Obtener proveedor activo por ID          |
| PUT    | `/api/proveedores/{id}/`                      | Actualizar proveedor y calificación      |
| DELETE | `/api/proveedores/{id}/`                      | Desactivar proveedor (soft-delete)       |
| GET    | `/api/proveedores/buscar/?ruc={ruc}`          | Buscar proveedor activo por RUC          |
| POST   | `/api/proveedores/{id}/activar/`              | Reactivar proveedor                      |
| PATCH  | `/api/proveedores/{id}/activar/`              | Reactivar proveedor                      |

#### Filtros (`GET /api/proveedores/`)

| Parámetro       | Descripción                                      |
|-----------------|--------------------------------------------------|
| `calificacion`  | Filtrar por calificación `A`, `B`, `C` o `D`    |

#### Validaciones

- RUC obligatorio de exactamente 11 dígitos.
- RUC único para proveedores activos o desactivados.
- Calificación limitada a `A`, `B`, `C` o `D`.
- Plazo de entrega mayor que cero.
- Correo electrónico con formato válido.
- Desactivación lógica mediante el campo `activo`.

#### Calificaciones

| Código | Descripción |
|--------|-------------|
| `A`    | Excelente   |
| `B`    | Bueno       |
| `C`    | Regular     |
| `D`    | Malo        |

---

### Servicio de Recepciones — Integrante 3

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
│   ├── proveedor_service.py
│   └── recepcion_service.py
├── 📁 presentacion/
│   ├── 📁 views/
│   │   ├── producto_views.py
│   │   ├── proveedor_views.py
│   │   └── recepcion_views.py
│   ├── 📁 serializers/
│   │   ├── producto_serializer.py
│   │   ├── proveedor_serializer.py
│   │   └── recepcion_serializer.py
│   └── 📁 urls/
│       ├── producto_urls.py
│       ├── proveedor_urls.py
│       └── recepcion_urls.py
├── 📁 tests/
│   ├── test_proveedor_api.py        # Pruebas de proveedores (5 casos)
│   └── test_recepcion_api.py        # Pruebas de recepciones (5 casos BDD)
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

### Proveedores

```bash
# Crear proveedor
curl -X POST http://localhost:8000/api/proveedores/ \
  -H "Content-Type: application/json" \
  -d '{
    "ruc": "20123456789",
    "razon_social": "Distribuidora Crisol SAC",
    "nombre_comercial": "Distribuidora Crisol",
    "direccion_calle": "Avenida Arequipa",
    "direccion_numero": "1234",
    "direccion_distrito": "Lince",
    "direccion_provincia": "Lima",
    "direccion_departamento": "Lima",
    "email": "ventas@distribuidoracrisol.pe",
    "telefono": "987654321",
    "especialidad": "Libros y material educativo",
    "plazo_entrega_dias": 5,
    "condiciones_pago": "Crédito a 30 días",
    "calificacion": "A",
    "es_nacional": true
  }'

# Buscar por RUC
curl "http://localhost:8000/api/proveedores/buscar/?ruc=20123456789"

# Filtrar por calificación
curl "http://localhost:8000/api/proveedores/?calificacion=A"

# Desactivar proveedor
curl -X DELETE http://localhost:8000/api/proveedores/1/

# Reactivar proveedor
curl -X POST http://localhost:8000/api/proveedores/1/activar/
```

#### Pruebas de proveedores

```bash
python manage.py test tests.test_proveedor_api
```

El módulo incluye cinco casos automatizados: creación con RUC válido, búsqueda por RUC, listado por calificación, actualización de calificación y desactivación lógica.

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

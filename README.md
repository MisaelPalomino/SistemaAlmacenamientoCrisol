# Sistema de Almacenamiento - Librerías Crisol

Proyecto Django con arquitectura en capas (DDD) para la gestión de inventario.

## Arquitectura

| Capa          | App             | Propósito                         |
|---------------|-----------------|-----------------------------------|
| Dominio       | `dominio`       | Modelos de datos (entidades)      |
| Aplicación    | `aplicacion`    | Servicios con lógica de negocio   |
| Presentación  | `presentacion`  | API REST (views, serializers)     |
| Infraestructura | `infraestructura` | Integraciones externas          |

## Servicios Implementados

### Productos (Integrante 1)
CRUD completo + alertas de stock, valor de inventario, filtros.

### Recepciones (Integrante 2) 

Registro y control de recepciones de productos.

## Servicio de Recepciones - Endpoints

### CRUD Básico

| Método | Endpoint                          | Descripción                     |
|--------|-----------------------------------|---------------------------------|
| POST   | `/api/recepciones/`               | Registrar una recepción         |
| GET    | `/api/recepciones/`               | Listar recepciones              |
| GET    | `/api/recepciones/{id}/`          | Obtener recepción por ID        |
| PUT    | `/api/recepciones/{id}/`          | Actualizar recepción            |

### Acciones de estado

| Método | Endpoint                                   | Descripción                          |
|--------|--------------------------------------------|--------------------------------------|
| POST   | `/api/recepciones/{id}/verificar/`         | Verificar (conforme → VERIFICADA, no conforme → PARCIAL) |
| POST   | `/api/recepciones/{id}/confirmar/`         | Confirmar (actualiza stock automáticamente)             |
| POST   | `/api/recepciones/{id}/rechazar/`          | Rechazar recepción                   |

### Filtros para listar (`GET /api/recepciones/`)

| Parámetro     | Descripción                          |
|---------------|--------------------------------------|
| `estado`      | Filtrar por estado                   |
| `producto_id` | Filtrar por producto                 |
| `proveedor_id`| Filtrar por proveedor                |
| `orden_compra`| Filtrar por orden de compra          |
| `desde`       | Fecha inicial (YYYY-MM-DD)           |
| `hasta`       | Fecha final (YYYY-MM-DD)             |
| `vista=simple`  | Respuesta simplificada            |

## Flujo de Estados

```
PENDIENTE ──→ EN_VERIFICACIÓN ──→ VERIFICADA ──→ CONFIRMADA
    │                                              (↑ stock)
    └──→ RECHAZADA
                    └──→ PARCIAL (si hay no conformes)
```

## Máquina de Estados

| Estado             | Descripción                                    |
|--------------------|------------------------------------------------|
| `PENDIENTE`        | Recién registrada, pendiente de verificación   |
| `EN_VERIFICACION`  | En proceso de verificación                     |
| `VERIFICADA`       | Verificada, todo conforme                      |
| `PARCIAL`          | Verificada con algunas unidades no conformes   |
| `CONFIRMADA`       | Confirmada, stock actualizado                  |
| `RECHAZADA`        | Rechazada                                      |

## Estructura de Archivos

```
📁 aplicacion/services/
  └── recepcion_service.py      # Lógica de negocio
📁 presentacion/views/
  └── recepcion_views.py         # Controladores REST
📁 presentacion/serializers/
  └── recepcion_serializer.py    # Serializadores
📁 presentacion/urls/
  └── recepcion_urls.py          # Rutas
📁 tests/
  └── test_recepcion_api.py      # Pruebas (5 casos BDD)
```

## Ejemplos de Uso

### 1. Registrar recepción

```bash
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
```

### 2. Verificar recepción (conforme)

```bash
curl -X POST http://localhost:8000/api/recepciones/1/verificar/ \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad_verificada": 30,
    "cantidad_conforme": 30,
    "cantidad_no_conforme": 0,
    "verificado_por": "Carlos López"
  }'
```

### 3. Verificar recepción (no conforme)

```bash
curl -X POST http://localhost:8000/api/recepciones/1/verificar/ \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad_verificada": 30,
    "cantidad_conforme": 25,
    "cantidad_no_conforme": 5,
    "verificado_por": "Carlos López"
  }'
```

### 4. Confirmar recepción (actualiza stock automáticamente)

```bash
curl -X POST http://localhost:8000/api/recepciones/1/confirmar/ \
  -H "Content-Type: application/json" \
  -d '{
    "confirmado_por": "María García"
  }'
```

### 5. Rechazar recepción

```bash
curl -X POST http://localhost:8000/api/recepciones/1/rechazar/ \
  -H "Content-Type: application/json" \
  -d '{
    "rechazado_por": "Admin",
    "observaciones": "Producto en mal estado"
  }'
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
pytest tests/test_recepcion_api.py -v --cov=.
```

# Sistema de Almacenamiento - Librerías Crisol

Proyecto Django con arquitectura en capas (DDD) para la gestión de inventario de Librerías Crisol.

## Arquitectura

| Capa             | App               | Propósito                         |
|------------------|-------------------|-----------------------------------|
| Dominio          | `dominio`         | Modelos de datos (entidades)      |
| Aplicación       | `aplicacion`      | Servicios con lógica de negocio   |
| Presentación     | `presentacion`    | API REST (views, serializers)     |
| Infraestructura  | `infraestructura` | Integraciones externas y RabbitMQ |

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

---

### Servicio de Reposiciones

Gestiona solicitudes de reposición, desde su registro y revisión hasta su ejecución, finalización o cancelación.

#### Endpoints

| Método | Endpoint                                  | Descripción                         |
|--------|-------------------------------------------|-------------------------------------|
| GET    | `/api/reposiciones/`                      | Listar solicitudes                  |
| POST   | `/api/reposiciones/`                      | Crear una solicitud                 |
| GET    | `/api/reposiciones/{id}/`                 | Obtener una solicitud               |
| PATCH  | `/api/reposiciones/{id}/revision/`        | Enviar a revisión                   |
| PATCH  | `/api/reposiciones/{id}/aprobar/`         | Aprobar la solicitud                |
| PATCH  | `/api/reposiciones/{id}/ejecutar/`        | Ejecutar la reposición              |
| PATCH  | `/api/reposiciones/{id}/completar/`       | Completar la reposición             |
| PATCH  | `/api/reposiciones/{id}/cancelar/`        | Cancelar la solicitud               |
| GET    | `/api/reposiciones/pendientes/`           | Listar solicitudes pendientes       |
| GET    | `/api/reposiciones/resumen/`              | Obtener el resumen de reposiciones  |

---

### Servicio de Incidencias

Registra, asigna, clasifica y da seguimiento a incidencias de inventario.

#### Endpoints

| Método | Endpoint                                  | Descripción                       |
|--------|-------------------------------------------|-----------------------------------|
| GET    | `/api/incidencias/`                       | Listar incidencias                |
| POST   | `/api/incidencias/`                       | Registrar una incidencia          |
| GET    | `/api/incidencias/{id}/`                  | Obtener una incidencia            |
| PATCH  | `/api/incidencias/{id}/asignar/`          | Asignar la incidencia             |
| PATCH  | `/api/incidencias/{id}/clasificar/`       | Modificar su prioridad            |
| PATCH  | `/api/incidencias/{id}/resolver/`         | Registrar la solución             |
| PATCH  | `/api/incidencias/{id}/cerrar/`           | Cerrar la incidencia              |
| PATCH  | `/api/incidencias/{id}/observacion/`      | Agregar una observación           |
| GET    | `/api/incidencias/activas/`               | Listar incidencias activas        |
| GET    | `/api/incidencias/resumen/`               | Obtener el resumen de incidencias |
| GET    | `/api/incidencias/tipos/`                 | Listar tipos disponibles          |
| GET    | `/api/incidencias/prioridades/`           | Listar prioridades disponibles    |
| GET    | `/api/incidencias/estados/`               | Listar estados disponibles        |

## Integración con RabbitMQ

El servicio de inventario funciona como consumidor de eventos para consultar productos con stock bajo. El flujo implementado es:

```text
Proceso BPM u otro productor
        │
        ▼
crisol.inventario.request
        │
        ▼
ProductoService.generar_alerta_stock_bajo()
        │
        ▼
crisol.inventario.response
```

### Contrato de solicitud

Cola: `crisol.inventario.request`

```json
{
  "tipo": "inventario.stock_bajo.consultar"
}
```

### Contrato de respuesta

Cola: `crisol.inventario.response`

```json
{
  "tipo": "inventario.stock_bajo.respuesta",
  "datos": {
    "alerta": false,
    "mensaje": "Todos los productos tienen stock adecuado",
    "total": 0
  }
}
```

Las colas son durables, las respuestas son persistentes y el consumidor utiliza confirmación manual mediante `ack`. Los mensajes JSON inválidos o con un tipo desconocido se rechazan mediante `nack` sin reencolarlos.

## Estructura del Proyecto

```
📦 SistemaAlmacenamientoCrisol/
├── 📁 almacen_inventario/           # Configuración Django
│   ├── settings.py
│   └── urls.py
├── 📁 dominio/models/               # Entidades del dominio
│   ├── producto.py
│   ├── proveedor.py
│   ├── recepcion.py
│   ├── incidencia.py
│   ├── reposicion.py
│   └── almacen.py
├── 📁 aplicacion/services/          # Casos de uso y lógica de negocio
│   ├── producto_service.py
│   ├── recepcion_service.py
│   ├── reposicion_service.py
│   └── incidencia_service.py
├── 📁 presentacion/
│   ├── 📁 views/
│   │   ├── producto_views.py
│   │   ├── recepcion_views.py
│   │   ├── reposicion_views.py
│   │   └── incidencia_views.py
│   ├── 📁 serializers/
│   │   ├── producto_serializer.py
│   │   ├── recepcion_serializer.py
│   │   ├── reposicion_serializer.py
│   │   └── incidencia_serializer.py
│   └── 📁 urls/
│       ├── producto_urls.py
│       ├── recepcion_urls.py
│       ├── reposicion_urls.py
│       └── incidencia_urls.py
├── 📁 infraestructura/
│   ├── 📁 rabbitmq/
│   │   └── inventario_consumer.py  # Consumidor de stock bajo
│   └── 📁 management/commands/
│       └── consumir_inventario.py  # Comando de Django
├── 📁 tests/
│   ├── test_producto_api.py
│   ├── test_recepcion_api.py
│   ├── test_incidencia_api.py
│   └── test_inventario_consumer.py
├── .env.example
├── manage.py
└── requirements.txt
```

## Instalación

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Linux o macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Configuración de RabbitMQ

1. Copiar el archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

2. Ajustar las variables según el entorno:

```env
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VIRTUAL_HOST=/
```

El archivo `.env` contiene la configuración local y no debe subirse al repositorio.

3. Con RabbitMQ en ejecución, iniciar el consumidor:

```powershell
python manage.py consumir_inventario
```

El proceso permanece escuchando la cola `crisol.inventario.request`. Se detiene con `Ctrl + C`.

## Ejecutar Pruebas

Todas las pruebas:

```powershell
python -m pytest tests/ -v
```

Pruebas del consumidor RabbitMQ:

```powershell
python -m pytest tests/test_inventario_consumer.py -v
```

Pruebas con cobertura:

```powershell
python -m pytest tests/ -v --cov=.
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

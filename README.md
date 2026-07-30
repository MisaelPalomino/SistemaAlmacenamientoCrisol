# Sistema de Almacenamiento - Librerías Crisol

Proyecto Django con arquitectura en capas (DDD) para la gestión de inventario de Librerías Crisol.

## Estado de la rama

Este documento corresponde a la rama acumulativa
`feature/openapi-swagger`. La rama parte del trabajo realizado en
`feature/rabbitmq-gestion-inventario`, por lo que contiene ambos avances:

| Avance | Estado | Evidencia principal |
|--------|--------|---------------------|
| Consumidor RabbitMQ de inventario | Completado | `infraestructura/rabbitmq/inventario_consumer.py` |
| Comando de administración de Django | Completado | `python manage.py consumir_inventario` |
| Configuración mediante variables de entorno | Completado | `.env.example` y `settings.RABBITMQ` |
| Confirmación manual y rechazo de mensajes | Completado | `ack` para mensajes válidos y `nack` sin reencolado para mensajes inválidos |
| Pruebas del consumidor | Completado | 5 casos en `tests/test_inventario_consumer.py` |
| Esquema OpenAPI 3 | Completado | `/api/schema/` |
| Swagger UI y ReDoc | Completado | `/api/docs/` y `/api/redoc/` |
| Pruebas de documentación API | Completado | 3 casos en `tests/test_openapi.py` |
| Integración con Bonita | Validada de extremo a extremo | Publicación, procesamiento y respuesta correlacionada mediante RabbitMQ |

La implementación BPM, los conectores de Bonita y la Living Application se
encuentran en el repositorio
[`MisaelPalomino/CrisolBonitaSoft`](https://github.com/MisaelPalomino/CrisolBonitaSoft),
rama `feature/rabbitmq-inventario`.

## Arquitectura

| Capa             | App               | Propósito                         |
|------------------|-------------------|-----------------------------------|
| Dominio          | `dominio`         | Modelos de datos (entidades)      |
| Aplicación       | `aplicacion`      | Servicios con lógica de negocio   |
| Presentación     | `presentacion`    | API REST (views, serializers)     |
| Infraestructura  | `infraestructura` | Integraciones externas y RabbitMQ |

## Documentación OpenAPI

Con el servidor Django en ejecución, la documentación interactiva está
disponible en:

| Recurso | URL |
|---------|-----|
| Esquema OpenAPI | `http://localhost:8000/api/schema/` |
| Swagger UI | `http://localhost:8000/api/docs/` |
| ReDoc | `http://localhost:8000/api/redoc/` |

Swagger UI y ReDoc utilizan recursos locales, por lo que no requieren conexión
a una CDN durante la demostración.

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

### Visión General
El Sistema de Almacenamiento Crisol está diseñado con una arquitectura en capas basada en DDD (Domain-Driven Design), implementada sobre Django REST Framework. 
Esta arquitectura refleja los procesos de negocio documentados en el análisis BPMN de Librerías Crisol S.A.C., abarcando la Gestión de Abastecimiento, Gestión de 
Inventario, Ventas en Tienda, Atención al Cliente, Marketing y Promoción, y Gestión de Pedidos Online.

Una característica fundamental de esta arquitectura es la ausencia de repositorios (repos), reemplazándolos directamente con el ORM de Django como capa de 
acceso a datos dentro de la infraestructura.

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
Bonita: Monitorear nivel de stock
        │  publica JSON + correlation_id
        ▼
RabbitMQ: crisol.inventario.request
        │
        ▼
Django: inventario_consumer
        │
        ├── ProductoService.generar_alerta_stock_bajo()
        │
        ├── ack de la solicitud válida
        │
        ▼
RabbitMQ: crisol.inventario.response
        │  conserva correlation_id
        ▼
Bonita: recibe la respuesta y actualiza stockBajo
        │
        ▼
Compuerta ¿Stock bajo?
        ├── No → Fin sin reposición
        └── Sí → Generar solicitud de reposición y notificar por correo
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

### Correlación de mensajes

Bonita genera un `correlation_id` para cada consulta. Django copia ese mismo
valor en la respuesta, permitiendo que el conector receptor de Bonita consuma
únicamente la respuesta correspondiente al caso en ejecución.

### Orden de ejecución para la demostración

1. Iniciar RabbitMQ y comprobar que el puerto AMQP `5672` esté disponible.
2. Iniciar el consumidor de Django:

   ```powershell
   python manage.py consumir_inventario
   ```

3. En otra terminal, iniciar la API y su documentación:

   ```powershell
   python manage.py runserver
   ```

4. Iniciar Bonita Studio y ejecutar `Proceso_Gestion_Inventario`.
5. Completar las tareas humanas hasta llegar a `Monitorear nivel de stock`.
6. Verificar en la terminal del consumidor el mensaje
   `Consulta de stock bajo procesada` junto con su `correlation_id`.
7. Comprobar que el proceso toma la salida correcta de la compuerta
   `¿Stock bajo?`.

### Servicio de Gestión de Pedidos Online (E-commerce) - Gonzalo R. Zapana 

El servicio de Gestión de Pedidos Online gestiona todo el ciclo de vida de las compras realizadas a través de la tienda virtual de Librerías Crisol S.A.C. 
Permite a los clientes seleccionar productos, realizar pagos electrónicos, y hacer seguimiento de sus pedidos desde la confirmación hasta la entrega final. 
El servicio integra pasarelas de pago (Izipay, Yape, Plin), couriers (Olva, Shalom, Serpost) y facturación electrónica con SUNAT, garantizando la consistencia 
del inventario en tiempo real mediante transacciones atónicas.

#### Endpoints

| Método | 	Endpoint	                 | Descripción                                             |
|--------|-------------------------------|---------------------------------------------------------| 
| POST	 | /api/pedidos/	             | Crear un nuevo pedido desde la tienda virtual           | 
| GET	 | /api/pedidos/{id}/	         | Obtener detalles de un pedido específico                | 
| GET	 | /api/pedidos/	             | Listar todos los pedidos del cliente autenticado        | 
| PUT	 | /api/pedidos/{id}/cancelar/	 | Cancelar un pedido (solo si está en estado "PENDIENTE") | 
| POST	 | /api/pedidos/{id}/pago/	     | Procesar el pago de un pedido                           | 
| GET	 | /api/pedidos/{id}/tracking/	 | Obtener estado de seguimiento del envío                 | 
| POST	 | /api/pedidos/{id}/devolucion/ | Solicitar devolución de un pedido entregado             | 

#### Filtros (GET /api/pedidos/)

| Parámetro	    | Tipo	  | Descripción	                      | Ejemplo                  | 
|---------------|---------|-----------------------------------|--------------------------| 
| estado	    | String  | Filtrar por estado del pedido	  | ?estado=PAGADO           | 
| fecha_inicio  | Date	  | Filtrar pedidos desde una fecha	  | ?fecha_inicio=2026-07-01 | 
| fecha_fin	    | Date	  | Filtrar pedidos hasta una fecha	  | ?fecha_fin=2026-07-31    | 
| cliente_dni	| String  | Filtrar por DNI del cliente	      | ?cliente_dni=12345678    | 
| metodo_pago	| String  | Filtrar por método de pago	      | ?metodo_pago=YAPE        | 

#### Ejemplos de consulta 

```bash
# Listar pedidos pendientes
GET /api/pedidos/?estado=PENDIENTE

# Listar pedidos de un cliente específico
GET /api/pedidos/?cliente_dni=12345678

# Listar pedidos pagados con Yape en julio 2026
GET /api/pedidos/?metodo_pago=YAPE&fecha_inicio=2026-07-01&fecha_fin=2026-07-31
```

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
│   ├── test_inventario_consumer.py
│   └── test_openapi.py
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

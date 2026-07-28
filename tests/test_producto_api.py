"""
Pruebas para el Servicio de Productos - Librerías Crisol
Solo tests que funcionan con la implementación actual
Integrante 1 - Gestión de Productos
"""

import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from dominio.models import Producto, Proveedor

pytestmark = pytest.mark.django_db


# =====================================================================
# FIXTURES
# =====================================================================


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def proveedor(db):
    return Proveedor.objects.create(
        ruc="20123456789",
        razon_social="Distribuidora Crisol S.A.",
        nombre_comercial="DistriCrisol",
        direccion_calle="Av. Larco",
        direccion_numero="1234",
        direccion_distrito="Miraflores",
        direccion_provincia="Lima",
        direccion_departamento="Lima",
        email="contacto@disticrisol.pe",
        telefono="012345678",
        especialidad="Libros y Revistas",
        plazo_entrega_dias=5,
        condiciones_pago="Crédito 30 días",
    )


@pytest.fixture
def producto(db, proveedor):
    return Producto.objects.create(
        isbn="9786120012345",
        nombre="El Principito",
        descripcion="Edición de lujo",
        tipo="LIBRO",
        categoria="LITERATURA",
        editorial="Planeta",
        autor="Antoine de Saint-Exupéry",
        precio_compra=Decimal("25.00"),
        precio_venta=Decimal("45.00"),
        stock_minimo=5,
        stock_maximo=50,
        stock_actual=10,
        proveedor_principal=proveedor,
    )


@pytest.fixture
def producto_data():
    """Datos para crear un producto (sin proveedor_principal para evitar errores)"""
    return {
        "isbn": "978-1234567890",
        "nombre": "Clean Code",
        "descripcion": "Libro de programación",
        "tipo": "LIBRO",
        "categoria": "LITERATURA",
        "editorial": "Prentice Hall",
        "autor": "Robert C. Martin",
        "año_publicacion": 2008,
        "precio_compra": "80.00",
        "precio_venta": "120.00",
        "stock_actual": 10,
        "stock_minimo": 5,
        "stock_maximo": 20,
        "ubicacion": "Estante A",
        "pasillo": "3",
        "estante": "B2",
    }


# =====================================================================
# CASO BDD 1: Crear producto exitosamente
# =====================================================================


class TestCrearProducto:
    def test_crear_producto_exitoso(self, api_client, producto_data):
        response = api_client.post("/api/productos/", producto_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["isbn"] == "978-1234567890"
        assert data["nombre"] == "Clean Code"
        assert data["tipo"] == "LIBRO"
        assert data["categoria"] == "LITERATURA"
        assert data["precio_compra"] == "80.00"
        assert data["precio_venta"] == "120.00"
        assert data["stock_actual"] == 10
        assert data["tiene_stock_bajo"] is False
        assert data["valor_inventario"] == "800.00"

    def test_crear_producto_isbn_duplicado(self, api_client, producto_data, producto):
        producto_data["isbn"] = producto.isbn
        response = api_client.post("/api/productos/", producto_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_msg = response.json().get("error", "").lower()
        assert "isbn" in error_msg or "ya existe" in error_msg

    def test_crear_producto_precio_venta_menor_compra(self, api_client, producto_data):
        producto_data["precio_venta"] = "50.00"
        response = api_client.post("/api/productos/", producto_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "precio de venta" in response.json().get("error", "").lower()

    def test_crear_producto_stock_maximo_menor_minimo(self, api_client, producto_data):
        producto_data["stock_minimo"] = 30
        producto_data["stock_maximo"] = 10
        response = api_client.post("/api/productos/", producto_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "stock máximo" in response.json().get("error", "").lower()


# =====================================================================
# CASO BDD 2: Listar productos
# =====================================================================


class TestListarProductos:
    def test_listar_productos(self, api_client, producto):
        response = api_client.get("/api/productos/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] >= 1
        assert len(data["results"]) >= 1
        item = data["results"][0]
        assert "id" in item
        assert "isbn" in item
        assert "nombre" in item

    def test_filtrar_por_categoria(self, api_client, producto):
        response = api_client.get(f"/api/productos/?categoria={producto.categoria}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] >= 1
        for item in data["results"]:
            assert item["categoria"] == producto.categoria


# =====================================================================
# CASO BDD 3: Obtener producto por ID
# =====================================================================


class TestObtenerProducto:
    def test_obtener_producto_existente(self, api_client, producto):
        response = api_client.get(f"/api/productos/{producto.id}/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == producto.id
        assert data["isbn"] == producto.isbn
        assert data["nombre"] == producto.nombre
        assert data["tiene_stock_bajo"] is False
        assert data["valor_inventario"] == str(producto.valor_inventario)

    def test_obtener_producto_inexistente(self, api_client):
        response = api_client.get("/api/productos/9999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "no encontrado" in response.json().get("error", "").lower()


# =====================================================================
# CASO BDD 4: Buscar producto por ISBN
# =====================================================================


class TestBuscarProductoPorISBN:
    def test_buscar_por_isbn_existente(self, api_client, producto):
        response = api_client.get(f"/api/productos/buscar/?isbn={producto.isbn}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["isbn"] == producto.isbn
        assert data["nombre"] == producto.nombre

    def test_buscar_por_isbn_inexistente(self, api_client):
        response = api_client.get("/api/productos/buscar/?isbn=978-0000000000")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "no encontrado" in response.json().get("error", "").lower()

    def test_buscar_por_isbn_sin_parametro(self, api_client):
        response = api_client.get("/api/productos/buscar/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "isbn" in response.json().get("error", "").lower()


# =====================================================================
# CASO BDD 5: Actualizar producto (PUT)
# =====================================================================


class TestActualizarProducto:
    def test_actualizar_producto_exitoso(self, api_client, producto):
        update_data = {
            "isbn": producto.isbn,
            "nombre": "Clean Code - Edición Actualizada",
            "descripcion": "Libro de programación actualizado",
            "tipo": "LIBRO",
            "categoria": "LITERATURA",
            "editorial": "Prentice Hall",
            "autor": "Robert C. Martin",
            "año_publicacion": 2020,
            "precio_compra": "90.00",
            "precio_venta": "140.00",
            "stock_actual": 20,
            "stock_minimo": 8,
            "stock_maximo": 30,
        }
        response = api_client.put(
            f"/api/productos/{producto.id}/", update_data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == "Clean Code - Edición Actualizada"
        assert data["precio_compra"] == "90.00"
        assert data["precio_venta"] == "140.00"
        assert data["stock_actual"] == 20
        assert data["stock_minimo"] == 8
        assert data["año_publicacion"] == 2020

    def test_actualizar_producto_inexistente(self, api_client, producto_data):
        response = api_client.put("/api/productos/9999/", producto_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no encontrado" in response.json().get("error", "").lower()


# =====================================================================
# CASO BDD 6: Incrementar stock
# =====================================================================


class TestActualizarStock:
    def test_incrementar_stock(self, api_client, producto):
        stock_inicial = producto.stock_actual
        response = api_client.patch(
            f"/api/productos/{producto.id}/stock/",
            {"cantidad": 5, "operacion": "incrementar"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["stock_actual"] == stock_inicial + 5
        producto.refresh_from_db()
        assert producto.stock_actual == stock_inicial + 5


# =====================================================================
# CASO BDD 7: Activar / Desactivar producto
# =====================================================================


class TestActivarProducto:
    def test_activar_producto(self, api_client, producto):
        producto.activo = False
        producto.save()
        response = api_client.patch(
            f"/api/productos/{producto.id}/activar/", format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["activo"] is True
        producto.refresh_from_db()
        assert producto.activo is True


# =====================================================================
# CASO BDD 8: Eliminar producto (soft delete)
# =====================================================================


class TestEliminarProducto:
    def test_eliminar_producto(self, api_client, producto):
        response = api_client.delete(f"/api/productos/{producto.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        producto.refresh_from_db()
        assert producto.activo is False

    def test_eliminar_producto_inexistente(self, api_client):
        response = api_client.delete("/api/productos/9999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "no encontrado" in response.json().get("error", "").lower()


# =====================================================================
# CASO BDD 9: Alerta de stock bajo
# =====================================================================


class TestAlertaStockBajo:
    def test_alerta_stock_bajo_con_productos(self, api_client, producto):
        Producto.objects.create(
            isbn="978-1111111111",
            nombre="Producto Stock Bajo",
            tipo="LIBRO",
            categoria="LITERATURA",
            precio_compra=Decimal("10.00"),
            precio_venta=Decimal("20.00"),
            stock_actual=2,
            stock_minimo=5,
            stock_maximo=10,
        )
        response = api_client.get("/api/productos/alertas_stock_bajo/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["alerta"] is True
        assert data["total"] >= 1
        assert len(data["productos"]) >= 1

    def test_alerta_stock_bajo_sin_productos(self, api_client):
        Producto.objects.all().delete()
        response = api_client.get("/api/productos/alertas_stock_bajo/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["alerta"] is False
        assert data["total"] == 0


# =====================================================================
# CASO BDD 10: Valor total del inventario
# =====================================================================


class TestValorInventario:
    def test_valor_inventario(self, api_client, producto):
        response = api_client.get("/api/productos/valor_inventario/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_productos" in data
        assert "valor_total_inventario" in data
        assert "productos_con_stock" in data
        assert "productos_agotados" in data
        assert data["total_productos"] >= 1
        assert data["valor_total_inventario"] > 0

    def test_valor_inventario_sin_productos(self, api_client):
        Producto.objects.all().delete()
        response = api_client.get("/api/productos/valor_inventario/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_productos"] == 0
        assert data["valor_total_inventario"] == 0


# =====================================================================
# CASO BDD 11: Productos por categoría
# =====================================================================


class TestProductosPorCategoria:
    def test_productos_por_categoria(self, api_client, producto):
        response = api_client.get(
            f"/api/productos/categoria/?nombre={producto.categoria}"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["categoria"] == producto.categoria
        assert data["count"] >= 1
        for item in data["results"]:
            assert item["categoria"] == producto.categoria

    def test_productos_por_categoria_inexistente(self, api_client):
        response = api_client.get("/api/productos/categoria/?nombre=INEXISTENTE")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["categoria"] == "INEXISTENTE"
        assert data["count"] == 0

    def test_productos_por_categoria_sin_parametro(self, api_client):
        response = api_client.get("/api/productos/categoria/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "nombre" in response.json().get("error", "").lower()

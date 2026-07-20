"""
Pruebas para el Servicio de Recepciones - Librerías Crisol

Formato: Pruebas de API (estilo Postman) + Casos BDD
"""
import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from dominio.models import Recepcion, Producto, Proveedor

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
        precio_compra=25.00,
        precio_venta=45.00,
        stock_minimo=5,
        stock_maximo=50,
        stock_actual=10,
        proveedor_principal=proveedor,
    )


@pytest.fixture
def recepcion_data(producto, proveedor):
    return {
        "orden_compra": "OC-2024-00123",
        "producto": producto.id,
        "proveedor": proveedor.id,
        "cantidad_esperada": 30,
        "cantidad_recibida": 30,
        "fecha_esperada_entrega": "2024-07-15",
        "creado_por": "Juan Pérez",
    }


# =====================================================================
# CASO BDD 1: Registrar recepción
# =====================================================================

class TestRegistrarRecepcion:
    """
    BDD - Caso 1: Registrar recepción
    Dado: Un producto y proveedor existentes
    Cuando: Se registra una nueva recepción
    Entonces: La recepción se crea con estado PENDIENTE
    """

    def test_crear_recepcion_exitosa(self, api_client, recepcion_data):
        response = api_client.post("/api/recepciones/", recepcion_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["orden_compra"] == "OC-2024-00123"
        assert data["estado"] == "PENDIENTE"
        assert data["numero_recepcion"].startswith("REC-")
        assert data["cantidad_esperada"] == 30
        assert data["cantidad_recibida"] == 30
        assert data["producto_nombre"] == "El Principito"
        assert data["proveedor_nombre"] == "Distribuidora Crisol S.A."

    def test_crear_recepcion_producto_inexistente(self, api_client, recepcion_data):
        recepcion_data["producto"] = 9999

        response = api_client.post("/api/recepciones/", recepcion_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_listar_recepciones(self, api_client, recepcion_data):
        api_client.post("/api/recepciones/", recepcion_data, format="json")

        response = api_client.get("/api/recepciones/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] >= 1
        assert len(data["results"]) >= 1

    def test_obtener_recepcion_por_id(self, api_client, recepcion_data):
        crear_resp = api_client.post("/api/recepciones/", recepcion_data, format="json")
        recepcion_id = crear_resp.json()["id"]

        response = api_client.get(f"/api/recepciones/{recepcion_id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == recepcion_id

    def test_obtener_recepcion_inexistente(self, api_client):
        response = api_client.get("/api/recepciones/9999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =====================================================================
# CASO BDD 2: Verificar recepción (conforme)
# =====================================================================

class TestVerificarRecepcionConforme:
    """
    BDD - Caso 2: Verificar recepción conforme
    Dado: Una recepción en estado PENDIENTE
    Cuando: Se verifica con cantidad_conforme = cantidad_verificada
    Entonces: La recepción pasa a estado VERIFICADA
    """

    def test_verificar_conforme(self, api_client, recepcion_data):
        crear_resp = api_client.post("/api/recepciones/", recepcion_data, format="json")
        recepcion_id = crear_resp.json()["id"]

        verify_data = {
            "cantidad_verificada": 30,
            "cantidad_conforme": 30,
            "cantidad_no_conforme": 0,
            "verificado_por": "Carlos López",
        }
        response = api_client.post(
            f"/api/recepciones/{recepcion_id}/verificar/", verify_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["estado"] == "VERIFICADA"
        assert data["conformidad"] is True
        assert data["cantidad_verificada"] == 30
        assert data["cantidad_conforme"] == 30
        assert data["cantidad_no_conforme"] == 0
        assert data["verificado_por"] == "Carlos López"


# =====================================================================
# CASO BDD 3: Verificar recepción (no conforme)
# =====================================================================

class TestVerificarRecepcionNoConforme:
    """
    BDD - Caso 3: Verificar recepción no conforme
    Dado: Una recepción en estado PENDIENTE
    Cuando: Se verifica con cantidad_no_conforme > 0
    Entonces: La recepción pasa a estado PARCIAL
    """

    def test_verificar_parcial(self, api_client, recepcion_data):
        crear_resp = api_client.post("/api/recepciones/", recepcion_data, format="json")
        recepcion_id = crear_resp.json()["id"]

        verify_data = {
            "cantidad_verificada": 30,
            "cantidad_conforme": 25,
            "cantidad_no_conforme": 5,
            "verificado_por": "Carlos López",
        }
        response = api_client.post(
            f"/api/recepciones/{recepcion_id}/verificar/", verify_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["estado"] == "PARCIAL"
        assert data["conformidad"] is False
        assert data["cantidad_verificada"] == 30
        assert data["cantidad_conforme"] == 25
        assert data["cantidad_no_conforme"] == 5

    def test_verificar_cantidad_excede_recibida(self, api_client, recepcion_data):
        crear_resp = api_client.post("/api/recepciones/", recepcion_data, format="json")
        recepcion_id = crear_resp.json()["id"]

        verify_data = {
            "cantidad_verificada": 35,
            "cantidad_conforme": 30,
            "cantidad_no_conforme": 5,
            "verificado_por": "Carlos López",
        }
        response = api_client.post(
            f"/api/recepciones/{recepcion_id}/verificar/", verify_data, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verificar_suma_inconsistente(self, api_client, recepcion_data):
        crear_resp = api_client.post("/api/recepciones/", recepcion_data, format="json")
        recepcion_id = crear_resp.json()["id"]

        verify_data = {
            "cantidad_verificada": 30,
            "cantidad_conforme": 20,
            "cantidad_no_conforme": 5,
            "verificado_por": "Carlos López",
        }
        response = api_client.post(
            f"/api/recepciones/{recepcion_id}/verificar/", verify_data, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =====================================================================
# CASO BDD 4: Confirmar recepción (actualiza stock)
# =====================================================================

class TestConfirmarRecepcion:
    """
    BDD - Caso 4: Confirmar recepción (actualiza stock)
    Dado: Una recepción en estado VERIFICADA
    Cuando: Se confirma la recepción
    Entonces: El stock del producto se incrementa y la recepción pasa a CONFIRMADA
    """

    def test_confirmar_actualiza_stock(self, api_client, producto, recepcion_data):
        stock_inicial = producto.stock_actual

        crear_resp = api_client.post("/api/recepciones/", recepcion_data, format="json")
        recepcion_id = crear_resp.json()["id"]

        api_client.post(
            f"/api/recepciones/{recepcion_id}/verificar/",
            {
                "cantidad_verificada": 30,
                "cantidad_conforme": 28,
                "cantidad_no_conforme": 2,
                "verificado_por": "Carlos López",
            },
            format="json",
        )

        response = api_client.post(
            f"/api/recepciones/{recepcion_id}/confirmar/",
            {"confirmado_por": "María García"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["estado"] == "CONFIRMADA"
        assert data["conformidad"] is True

        producto.refresh_from_db()
        assert producto.stock_actual == stock_inicial + 28

    def test_confirmar_sin_verificar(self, api_client, recepcion_data):
        crear_resp = api_client.post("/api/recepciones/", recepcion_data, format="json")
        recepcion_id = crear_resp.json()["id"]

        response = api_client.post(
            f"/api/recepciones/{recepcion_id}/confirmar/",
            {"confirmado_por": "María García"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =====================================================================
# CASO BDD 5: Rechazar recepción
# =====================================================================

class TestRechazarRecepcion:
    """
    BDD - Caso 5: Rechazar recepción
    Dado: Una recepción en estado PENDIENTE
    Cuando: Se rechaza la recepción
    Entonces: La recepción pasa a estado RECHAZADA
    """

    def test_rechazar_recepcion(self, api_client, recepcion_data):
        crear_resp = api_client.post("/api/recepciones/", recepcion_data, format="json")
        recepcion_id = crear_resp.json()["id"]

        response = api_client.post(
            f"/api/recepciones/{recepcion_id}/rechazar/",
            {
                "rechazado_por": "Admin",
                "observaciones": "Producto en mal estado",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["estado"] == "RECHAZADA"
        assert data["conformidad"] is False
        assert "Producto en mal estado" in data["observaciones"]

    def test_rechazar_ya_confirmada(self, api_client, producto, recepcion_data):
        crear_resp = api_client.post("/api/recepciones/", recepcion_data, format="json")
        recepcion_id = crear_resp.json()["id"]

        api_client.post(
            f"/api/recepciones/{recepcion_id}/verificar/",
            {
                "cantidad_verificada": 30,
                "cantidad_conforme": 30,
                "cantidad_no_conforme": 0,
                "verificado_por": "Carlos López",
            },
            format="json",
        )
        api_client.post(
            f"/api/recepciones/{recepcion_id}/confirmar/",
            {"confirmado_por": "María García"},
            format="json",
        )

        response = api_client.post(
            f"/api/recepciones/{recepcion_id}/rechazar/",
            {"rechazado_por": "Admin", "observaciones": "Ya no se necesita"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =====================================================================
# PRUEBAS ADICIONALES - Listar por estado / producto
# =====================================================================

class TestListarRecepciones:
    """
    Pruebas para listar recepciones con filtros
    """

    def test_filtrar_por_estado(self, api_client, recepcion_data):
        api_client.post("/api/recepciones/", recepcion_data, format="json")

        response = api_client.get("/api/recepciones/?estado=PENDIENTE")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(r["estado"] == "PENDIENTE" for r in data["results"])

    def test_filtrar_por_producto(self, api_client, producto, recepcion_data):
        api_client.post("/api/recepciones/", recepcion_data, format="json")

        response = api_client.get(f"/api/recepciones/?producto_id={producto.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 1

    def test_listar_simple(self, api_client, recepcion_data):
        api_client.post("/api/recepciones/", recepcion_data, format="json")

        response = api_client.get("/api/recepciones/?vista=simple")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        if data["count"] > 0:
            item = data["results"][0]
            assert "producto_nombre" in item
            assert "proveedor_nombre" in item
            assert "producto_isbn" not in item

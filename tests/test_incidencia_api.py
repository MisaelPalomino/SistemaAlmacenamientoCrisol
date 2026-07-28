"""
Pruebas para el Servicio de Incidencias - Librerías Crisol
Integrante 4 - Gestión de Incidencias
"""

import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from dominio.models import Incidencia, Producto, Proveedor

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
def incidencia_data(producto):
    return {
        "codigo_incidencia": "INC-2026-001",
        "producto_id": producto.id,
        "tipo": "PRODUCTO_DETERIORADO",
        "descripcion": "Producto llegó con daños en la cubierta",
        "cantidad_afectada": 3,
        "responsable": "Juan Perez",
        "prioridad": "MEDIA",
    }


# =====================================================================
# CASO BDD 1: Registrar incidencia
# =====================================================================


class TestRegistrarIncidencia:
    def test_crear_incidencia_exitosa(self, api_client, incidencia_data):
        response = api_client.post("/api/incidencias/", incidencia_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["codigo_incidencia"] == "INC-2026-001"
        assert data["estado"] == "REGISTRADA"
        assert data["tipo"] == "PRODUCTO_DETERIORADO"
        assert data["cantidad_afectada"] == 3

    def test_crear_incidencia_producto_inexistente(self, api_client, incidencia_data):
        incidencia_data["producto_id"] = 9999
        response = api_client.post("/api/incidencias/", incidencia_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "producto" in response.json().get("error", "").lower()


# =====================================================================
# CASO BDD 2: Listar incidencias
# =====================================================================


class TestListarIncidencias:
    def test_listar_incidencias(self, api_client, incidencia_data):
        api_client.post("/api/incidencias/", incidencia_data, format="json")
        response = api_client.get("/api/incidencias/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] >= 1
        assert len(data["results"]) >= 1


# =====================================================================
# CASO BDD 3: Obtener incidencia por ID
# =====================================================================


class TestObtenerIncidencia:
    def test_obtener_incidencia_existente(self, api_client, incidencia_data):
        crear_resp = api_client.post(
            "/api/incidencias/", incidencia_data, format="json"
        )
        incidencia_id = crear_resp.json()["id"]
        response = api_client.get(f"/api/incidencias/{incidencia_id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == incidencia_id

    def test_obtener_incidencia_inexistente(self, api_client):
        response = api_client.get("/api/incidencias/9999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =====================================================================
# CASO BDD 4: Asignar incidencia
# =====================================================================


class TestAsignarIncidencia:
    def test_asignar_incidencia(self, api_client, incidencia_data):
        crear_resp = api_client.post(
            "/api/incidencias/", incidencia_data, format="json"
        )
        incidencia_id = crear_resp.json()["id"]
        response = api_client.patch(
            f"/api/incidencias/{incidencia_id}/asignar/",
            {"asignado_a": "Maria Lopez"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["asignado_a"] == "Maria Lopez"
        assert data["estado"] == "EN_REVISION"

    def test_asignar_incidencia_sin_campo(self, api_client, incidencia_data):
        crear_resp = api_client.post(
            "/api/incidencias/", incidencia_data, format="json"
        )
        incidencia_id = crear_resp.json()["id"]
        response = api_client.patch(
            f"/api/incidencias/{incidencia_id}/asignar/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =====================================================================
# CASO BDD 5: Clasificar incidencia
# =====================================================================


class TestClasificarIncidencia:
    def test_clasificar_incidencia(self, api_client, incidencia_data):
        crear_resp = api_client.post(
            "/api/incidencias/", incidencia_data, format="json"
        )
        incidencia_id = crear_resp.json()["id"]
        response = api_client.patch(
            f"/api/incidencias/{incidencia_id}/clasificar/",
            {"prioridad": "CRITICA"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["prioridad"] == "CRITICA"

    def test_clasificar_incidencia_prioridad_invalida(
        self, api_client, incidencia_data
    ):
        crear_resp = api_client.post(
            "/api/incidencias/", incidencia_data, format="json"
        )
        incidencia_id = crear_resp.json()["id"]
        response = api_client.patch(
            f"/api/incidencias/{incidencia_id}/clasificar/",
            {"prioridad": "INVALIDA"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =====================================================================
# CASO BDD 6: Resolver incidencia
# =====================================================================


class TestResolverIncidencia:
    def test_resolver_incidencia(self, api_client, incidencia_data):
        crear_resp = api_client.post(
            "/api/incidencias/", incidencia_data, format="json"
        )
        incidencia_id = crear_resp.json()["id"]
        # Primero asignar para poder resolver
        api_client.patch(
            f"/api/incidencias/{incidencia_id}/asignar/",
            {"asignado_a": "Maria Lopez"},
            format="json",
        )
        response = api_client.patch(
            f"/api/incidencias/{incidencia_id}/resolver/",
            {"solucion": "Se reemplazaron los productos dañados"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["estado"] == "RESUELTA"
        assert data["solucion_aplicada"] == "Se reemplazaron los productos dañados"

    def test_resolver_incidencia_sin_solucion(self, api_client, incidencia_data):
        crear_resp = api_client.post(
            "/api/incidencias/", incidencia_data, format="json"
        )
        incidencia_id = crear_resp.json()["id"]
        api_client.patch(
            f"/api/incidencias/{incidencia_id}/asignar/",
            {"asignado_a": "Maria Lopez"},
            format="json",
        )
        response = api_client.patch(
            f"/api/incidencias/{incidencia_id}/resolver/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =====================================================================
# CASO BDD 7: Cerrar incidencia
# =====================================================================


class TestCerrarIncidencia:
    def test_cerrar_incidencia(self, api_client, incidencia_data):
        crear_resp = api_client.post(
            "/api/incidencias/", incidencia_data, format="json"
        )
        incidencia_id = crear_resp.json()["id"]
        api_client.patch(
            f"/api/incidencias/{incidencia_id}/asignar/",
            {"asignado_a": "Maria Lopez"},
            format="json",
        )
        api_client.patch(
            f"/api/incidencias/{incidencia_id}/resolver/",
            {"solucion": "Se reemplazaron los productos"},
            format="json",
        )
        response = api_client.patch(
            f"/api/incidencias/{incidencia_id}/cerrar/",
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["estado"] == "CERRADA"


# =====================================================================
# CASO BDD 8: Listar incidencias activas
# =====================================================================


class TestIncidenciasActivas:
    def test_listar_activas(self, api_client, incidencia_data):
        api_client.post("/api/incidencias/", incidencia_data, format="json")
        response = api_client.get("/api/incidencias/activas/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] >= 1


# =====================================================================
# CASO BDD 9: Resumen de incidencias
# =====================================================================


class TestResumenIncidencias:
    def test_resumen(self, api_client, incidencia_data):
        api_client.post("/api/incidencias/", incidencia_data, format="json")
        response = api_client.get("/api/incidencias/resumen/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_incidencias" in data
        assert "activas" in data
        assert "cerradas" in data
        assert data["total_incidencias"] >= 1


# =====================================================================
# CASO BDD 10: Listar tipos, prioridades y estados
# =====================================================================


class TestCatalogosIncidencias:
    def test_listar_tipos(self, api_client):
        response = api_client.get("/api/incidencias/tipos/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert "codigo" in data[0]
        assert "descripcion" in data[0]

    def test_listar_prioridades(self, api_client):
        response = api_client.get("/api/incidencias/prioridades/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0

    def test_listar_estados(self, api_client):
        response = api_client.get("/api/incidencias/estados/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
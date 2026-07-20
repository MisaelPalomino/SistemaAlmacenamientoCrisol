from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from dominio.models import Proveedor


class ProveedorAPITests(APITestCase):
    def datos_proveedor(self, ruc="20123456789", calificacion="B"):
        return {
            "ruc": ruc,
            "razon_social": "Distribuidora Crisol SAC",
            "nombre_comercial": "Distribuidora Crisol",
            "direccion_calle": "Avenida Arequipa",
            "direccion_numero": "1234",
            "direccion_distrito": "Lince",
            "direccion_provincia": "Lima",
            "direccion_departamento": "Lima",
            "direccion_codigo_postal": "15046",
            "direccion_referencia": "Cerca del parque principal",
            "email": "ventas@distribuidoracrisol.pe",
            "telefono": "987654321",
            "telefono_alternativo": "014567890",
            "especialidad": "Libros y material educativo",
            "plazo_entrega_dias": 5,
            "condiciones_pago": "Crédito a 30 días",
            "calificacion": calificacion,
            "es_nacional": True,
        }

    def crear_proveedor(self, ruc="20123456789", calificacion="B"):
        return Proveedor.objects.create(
            **self.datos_proveedor(ruc=ruc, calificacion=calificacion)
        )

    def test_crear_proveedor_con_ruc_valido(self):
        respuesta = self.client.post(
            reverse("proveedor-list"),
            self.datos_proveedor(),
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["ruc"], "20123456789")
        self.assertTrue(
            Proveedor.objects.filter(ruc="20123456789", activo=True).exists()
        )

    def test_buscar_proveedor_por_ruc(self):
        proveedor = self.crear_proveedor()

        respuesta = self.client.get(
            reverse("proveedor-buscar"),
            {"ruc": proveedor.ruc},
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["id"], proveedor.id)
        self.assertEqual(respuesta.data["ruc"], proveedor.ruc)

    def test_listar_proveedores_por_calificacion(self):
        proveedor_a = self.crear_proveedor(
            ruc="20123456789",
            calificacion="A",
        )
        self.crear_proveedor(
            ruc="20987654321",
            calificacion="C",
        )

        respuesta = self.client.get(
            reverse("proveedor-list"),
            {"calificacion": "A"},
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["id"], proveedor_a.id)
        self.assertEqual(respuesta.data["results"][0]["calificacion"], "A")

    def test_actualizar_calificacion_de_proveedor(self):
        proveedor = self.crear_proveedor(calificacion="B")
        datos_actualizados = self.datos_proveedor(calificacion="A")

        respuesta = self.client.put(
            reverse("proveedor-detail", args=[proveedor.id]),
            datos_actualizados,
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        proveedor.refresh_from_db()
        self.assertEqual(proveedor.calificacion, "A")
        self.assertEqual(respuesta.data["calificacion"], "A")

    def test_desactivar_proveedor(self):
        proveedor = self.crear_proveedor()

        respuesta = self.client.delete(
            reverse("proveedor-detail", args=[proveedor.id])
        )

        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        proveedor.refresh_from_db()
        self.assertFalse(proveedor.activo)

        listado = self.client.get(reverse("proveedor-list"))
        ids_activos = [item["id"] for item in listado.data["results"]]
        self.assertNotIn(proveedor.id, ids_activos)

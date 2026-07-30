from django.urls import reverse


def test_esquema_openapi_disponible(client):
    response = client.get(reverse("api-schema"))

    assert response.status_code == 200
    assert b"openapi: 3.0.3" in response.content
    assert b"/api/productos/" in response.content
    assert b"/api/recepciones/" in response.content
    assert b"/api/reposiciones/" in response.content
    assert b"/api/incidencias/" in response.content


def test_swagger_ui_disponible(client):
    response = client.get(reverse("swagger-ui"))

    assert response.status_code == 200
    assert b"swagger-ui" in response.content.lower()
    assert reverse("api-schema").encode() in response.content


def test_redoc_disponible(client):
    response = client.get(reverse("redoc"))

    assert response.status_code == 200
    assert b"redoc" in response.content.lower()
    assert reverse("api-schema").encode() in response.content

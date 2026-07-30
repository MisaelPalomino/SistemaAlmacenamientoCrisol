"""
Vistas para Incidencias con ViewSet
Integrante 4 - Gestión de Incidencias
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from aplicacion.services.incidencia_service import IncidenciaService
from dominio.models.incidencia import Incidencia
from presentacion.serializers.incidencia_serializer import (
    IncidenciaSerializer,
    IncidenciaListSerializer,
    IncidenciaEstadoSerializer,
    IncidenciaTipoSerializer,
)


class IncidenciaViewSet(viewsets.ViewSet):
    """
    ViewSet para Incidencias
    """

    queryset = Incidencia.objects.none()
    serializer_class = IncidenciaSerializer

    def list(self, request):
        """GET /api/incidencias/ - Listar incidencias"""
        try:
            filtros = {
                "tipo": request.query_params.get("tipo"),
                "estado": request.query_params.get("estado"),
                "prioridad": request.query_params.get("prioridad"),
                "producto_id": request.query_params.get("producto_id"),
                "search": request.query_params.get("search"),
            }
            filtros = {k: v for k, v in filtros.items() if v is not None}

            incidencias = IncidenciaService.listar_incidencias(filtros)

            if request.query_params.get("format") == "simple":
                serializer = IncidenciaListSerializer(incidencias, many=True)
            else:
                serializer = IncidenciaSerializer(incidencias, many=True)

            return Response({"count": incidencias.count(), "results": serializer.data})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        """POST /api/incidencias/ - Registrar incidencia"""
        try:
            incidencia = IncidenciaService.crear_incidencia(request.data)
            serializer = IncidenciaSerializer(incidencia)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """GET /api/incidencias/{id}/ - Obtener incidencia"""
        incidencia = IncidenciaService.obtener_incidencia_por_id(pk)
        if not incidencia:
            return Response(
                {"error": f"Incidencia con ID {pk} no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = IncidenciaSerializer(incidencia)
        return Response(serializer.data)

    # ========== ACCIONES PERSONALIZADAS ==========

    @action(detail=True, methods=["patch"])
    def asignar(self, request, pk=None):
        """
        PATCH /api/incidencias/{id}/asignar/ - Asignar incidencia
        Body: {"asignado_a": "Juan Perez"}
        """
        try:
            asignado_a = request.data.get("asignado_a")

            if not asignado_a:
                return Response(
                    {"error": 'El campo "asignado_a" es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            incidencia = IncidenciaService.asignar_incidencia(pk, asignado_a)
            serializer = IncidenciaSerializer(incidencia)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def clasificar(self, request, pk=None):
        """
        PATCH /api/incidencias/{id}/clasificar/ - Clasificar incidencia
        Body: {"prioridad": "CRITICA"}
        """
        try:
            nueva_prioridad = request.data.get("prioridad")

            if not nueva_prioridad:
                return Response(
                    {"error": 'El campo "prioridad" es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            incidencia = IncidenciaService.clasificar_incidencia(pk, nueva_prioridad)
            serializer = IncidenciaSerializer(incidencia)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def resolver(self, request, pk=None):
        """
        PATCH /api/incidencias/{id}/resolver/ - Resolver incidencia
        Body: {"solucion": "Se reemplazó el producto dañado"}
        """
        try:
            solucion = request.data.get("solucion")

            if not solucion:
                return Response(
                    {"error": 'El campo "solucion" es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            incidencia = IncidenciaService.resolver_incidencia(pk, solucion)
            serializer = IncidenciaSerializer(incidencia)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def cerrar(self, request, pk=None):
        """
        PATCH /api/incidencias/{id}/cerrar/ - Cerrar incidencia
        """
        try:
            incidencia = IncidenciaService.cerrar_incidencia(pk)
            serializer = IncidenciaSerializer(incidencia)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def observacion(self, request, pk=None):
        """
        PATCH /api/incidencias/{id}/observacion/ - Agregar observación
        Body: {"observacion": "Descripción de la observación"}
        """
        try:
            observacion = request.data.get("observacion")

            if not observacion:
                return Response(
                    {"error": 'El campo "observacion" es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            incidencia = IncidenciaService.agregar_observacion(pk, observacion)
            serializer = IncidenciaSerializer(incidencia)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def activas(self, request):
        """
        GET /api/incidencias/activas/ - Listar incidencias activas
        """
        incidencias = IncidenciaService.listar_incidencias_activas()
        serializer = IncidenciaListSerializer(incidencias, many=True)
        return Response({"count": incidencias.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def resumen(self, request):
        """
        GET /api/incidencias/resumen/ - Resumen de incidencias
        """
        resumen = IncidenciaService.resumen_incidencias()
        return Response(resumen)

    @action(detail=False, methods=["get"])
    def tipos(self, request):
        """
        GET /api/incidencias/tipos/ - Listar tipos de incidencia
        """
        tipos = IncidenciaService.listar_tipos()
        data = [{"codigo": t[0], "descripcion": t[1]} for t in tipos]
        return Response(data)

    @action(detail=False, methods=["get"])
    def prioridades(self, request):
        """
        GET /api/incidencias/prioridades/ - Listar prioridades
        """
        prioridades = IncidenciaService.listar_prioridades()
        data = [{"codigo": p[0], "descripcion": p[1]} for p in prioridades]
        return Response(data)

    @action(detail=False, methods=["get"])
    def estados(self, request):
        """
        GET /api/incidencias/estados/ - Listar estados
        """
        estados = IncidenciaService.listar_estados()
        data = [{"codigo": e[0], "descripcion": e[1]} for e in estados]
        return Response(data)

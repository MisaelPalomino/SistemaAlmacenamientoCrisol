"""
Vistas para Solicitudes de Reposición con ViewSet
Integrante 5 - Gestión de Reposiciones
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from aplicacion.services.reposicion_service import ReposicionService
from dominio.models.reposicion import SolicitudReposicion
from presentacion.serializers.reposicion_serializer import (
    SolicitudReposicionSerializer,
    ReposicionListSerializer,
    ReposicionEstadoSerializer,
)


class ReposicionViewSet(viewsets.ViewSet):
    """
    ViewSet para Solicitudes de Reposición
    """

    queryset = SolicitudReposicion.objects.none()
    serializer_class = SolicitudReposicionSerializer

    def list(self, request):
        """GET /api/reposiciones/ - Listar solicitudes"""
        try:
            filtros = {
                "estado": request.query_params.get("estado"),
                "prioridad": request.query_params.get("prioridad"),
                "producto_id": request.query_params.get("producto_id"),
                "search": request.query_params.get("search"),
            }
            filtros = {k: v for k, v in filtros.items() if v is not None}

            solicitudes = ReposicionService.listar_solicitudes(filtros)

            if request.query_params.get("format") == "simple":
                serializer = ReposicionListSerializer(solicitudes, many=True)
            else:
                serializer = SolicitudReposicionSerializer(solicitudes, many=True)

            return Response({"count": solicitudes.count(), "results": serializer.data})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        """POST /api/reposiciones/ - Crear solicitud"""
        try:
            solicitud = ReposicionService.crear_solicitud(request.data)
            serializer = SolicitudReposicionSerializer(solicitud)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """GET /api/reposiciones/{id}/ - Obtener solicitud"""
        solicitud = ReposicionService.obtener_solicitud_por_id(pk)
        if not solicitud:
            return Response(
                {"error": f"Solicitud con ID {pk} no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = SolicitudReposicionSerializer(solicitud)
        return Response(serializer.data)

    # ========== ACCIONES PERSONALIZADAS ==========

    @action(detail=True, methods=["patch"])
    def aprobar(self, request, pk=None):
        """
        PATCH /api/reposiciones/{id}/aprobar/ - Aprobar solicitud
        Body: {"aprobado_por": "Admin", "cantidad_aprobada": 10}
        """
        try:
            aprobado_por = request.data.get("aprobado_por")
            cantidad_aprobada = request.data.get("cantidad_aprobada")

            if not aprobado_por:
                return Response(
                    {"error": 'El campo "aprobado_por" es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            solicitud = ReposicionService.aprobar_solicitud(
                pk, aprobado_por, cantidad_aprobada
            )
            serializer = SolicitudReposicionSerializer(solicitud)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def ejecutar(self, request, pk=None):
        """
        PATCH /api/reposiciones/{id}/ejecutar/ - Ejecutar reposición
        Body: {"ejecutado_por": "Logistica"}
        """
        try:
            ejecutado_por = request.data.get("ejecutado_por")

            if not ejecutado_por:
                return Response(
                    {"error": 'El campo "ejecutado_por" es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            solicitud = ReposicionService.ejecutar_reposicion(pk, ejecutado_por)
            serializer = SolicitudReposicionSerializer(solicitud)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def completar(self, request, pk=None):
        """
        PATCH /api/reposiciones/{id}/completar/ - Completar reposición
        Body: {"cantidad_repuesta": 15}
        """
        try:
            cantidad_repuesta = request.data.get("cantidad_repuesta")

            if cantidad_repuesta is None:
                return Response(
                    {"error": 'El campo "cantidad_repuesta" es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            solicitud = ReposicionService.completar_reposicion(
                pk, int(cantidad_repuesta)
            )
            serializer = SolicitudReposicionSerializer(solicitud)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def cancelar(self, request, pk=None):
        """
        PATCH /api/reposiciones/{id}/cancelar/ - Cancelar solicitud
        Body: {"motivo": "Cambio de proveedor"}
        """
        try:
            motivo = request.data.get("motivo")

            if not motivo:
                return Response(
                    {"error": 'El campo "motivo" es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            solicitud = ReposicionService.cancelar_solicitud(pk, motivo)
            serializer = SolicitudReposicionSerializer(solicitud)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def revision(self, request, pk=None):
        """
        PATCH /api/reposiciones/{id}/revision/ - Enviar a revisión
        """
        try:
            solicitud = ReposicionService.enviar_revision(pk)
            serializer = SolicitudReposicionSerializer(solicitud)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def pendientes(self, request):
        """
        GET /api/reposiciones/pendientes/ - Listar solicitudes pendientes
        """
        solicitudes = ReposicionService.listar_solicitudes_pendientes()
        serializer = ReposicionListSerializer(solicitudes, many=True)
        return Response({"count": solicitudes.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def resumen(self, request):
        """
        GET /api/reposiciones/resumen/ - Resumen de solicitudes
        """
        resumen = ReposicionService.resumen_solicitudes()
        return Response(resumen)

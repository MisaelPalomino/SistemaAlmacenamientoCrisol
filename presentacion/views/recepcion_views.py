from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from aplicacion.services.recepcion_service import RecepcionService
from dominio.models.recepcion import Recepcion
from presentacion.serializers.recepcion_serializer import (
    RecepcionSerializer,
    RecepcionListSerializer,
)


class RecepcionViewSet(viewsets.ViewSet):

    queryset = Recepcion.objects.none()
    serializer_class = RecepcionSerializer

    def list(self, request):
        try:
            filtros = {
                "estado": request.query_params.get("estado"),
                "producto_id": request.query_params.get("producto_id"),
                "proveedor_id": request.query_params.get("proveedor_id"),
                "orden_compra": request.query_params.get("orden_compra"),
                "desde": request.query_params.get("desde"),
                "hasta": request.query_params.get("hasta"),
            }
            filtros = {k: v for k, v in filtros.items() if v is not None}

            recepciones = RecepcionService.listar_recepciones(filtros)

            if request.query_params.get("vista") == "simple":
                serializer = RecepcionListSerializer(recepciones, many=True)
            else:
                serializer = RecepcionSerializer(recepciones, many=True)

            return Response({"count": recepciones.count(), "results": serializer.data})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        try:
            recepcion = RecepcionService.crear_recepcion(request.data)
            serializer = RecepcionSerializer(recepcion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        recepcion = RecepcionService.obtener_recepcion_por_id(pk)
        if not recepcion:
            return Response(
                {"error": f"Recepción con ID {pk} no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = RecepcionSerializer(recepcion)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            recepcion = RecepcionService.actualizar_recepcion(pk, request.data)
            serializer = RecepcionSerializer(recepcion)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def verificar(self, request, pk=None):
        try:
            usuario = request.data.get("verificado_por", request.data.get("creado_por", ""))
            recepcion = RecepcionService.verificar_recepcion(pk, request.data, usuario)
            serializer = RecepcionSerializer(recepcion)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        try:
            usuario = request.data.get("confirmado_por", "")
            if not usuario:
                return Response(
                    {"error": "El campo 'confirmado_por' es obligatorio"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            recepcion = RecepcionService.confirmar_recepcion(pk, usuario)
            serializer = RecepcionSerializer(recepcion)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        try:
            usuario = request.data.get("rechazado_por", request.data.get("creado_por", ""))
            observaciones = request.data.get("observaciones", "")
            recepcion = RecepcionService.rechazar_recepcion(pk, usuario, observaciones)
            serializer = RecepcionSerializer(recepcion)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

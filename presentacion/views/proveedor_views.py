from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from aplicacion.services.proveedor_service import ProveedorService
from presentacion.serializers.proveedor_serializer import ProveedorSerializer


class ProveedorViewSet(viewsets.ViewSet):
    def list(self, request):
        filtros = {
            "calificacion": request.query_params.get("calificacion"),
        }
        filtros = {campo: valor for campo, valor in filtros.items() if valor}

        try:
            proveedores = ProveedorService.listar_proveedores(filtros)
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProveedorSerializer(proveedores, many=True)
        return Response(
            {
                "count": proveedores.count(),
                "results": serializer.data,
            }
        )

    def create(self, request):
        serializer = ProveedorSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            proveedor = ProveedorService.crear_proveedor(
                serializer.validated_data
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ProveedorSerializer(proveedor).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        proveedor = ProveedorService.obtener_proveedor_por_id(pk)
        if proveedor is None:
            return Response(
                {"error": f"Proveedor activo con ID {pk} no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(ProveedorSerializer(proveedor).data)

    def update(self, request, pk=None):
        proveedor_actual = ProveedorService.obtener_proveedor_por_id(pk)
        if proveedor_actual is None:
            return Response(
                {"error": f"Proveedor activo con ID {pk} no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProveedorSerializer(
            proveedor_actual,
            data=request.data,
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            proveedor = ProveedorService.actualizar_proveedor(
                pk,
                serializer.validated_data,
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ProveedorSerializer(proveedor).data)

    def destroy(self, request, pk=None):
        desactivado = ProveedorService.desactivar_proveedor(pk)
        if not desactivado:
            return Response(
                {"error": f"Proveedor activo con ID {pk} no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def buscar(self, request):
        ruc = request.query_params.get("ruc")
        if not ruc:
            return Response(
                {"error": "El parámetro ruc es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            proveedor = ProveedorService.buscar_proveedor_por_ruc(ruc)
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if proveedor is None:
            return Response(
                {"error": f"Proveedor activo con RUC {ruc} no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(ProveedorSerializer(proveedor).data)

    @action(detail=True, methods=["post", "patch"])
    def activar(self, request, pk=None):
        try:
            proveedor = ProveedorService.activar_proveedor(pk)
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ProveedorSerializer(proveedor).data)

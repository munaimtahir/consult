from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


class APIRootView(APIView):
    """
    API root endpoint for the Hospital Consult System.
    """
    def get(self, request):
        return Response({
            "detail": "Hospital Consult System API root - TODO: expand."
        })


# TODO: implement additional API views

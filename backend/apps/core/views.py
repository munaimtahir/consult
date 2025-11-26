from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


class APIRootView(APIView):
    """API root endpoint for the Hospital Consult System.

    This view provides a basic entry point to the API, returning a
    simple JSON response.
    """

    def get(self, request):
        """Handles GET requests to the API root.

        Args:
            request: The Django HttpRequest object.

        Returns:
            A DRF Response object with a welcome message.
        """
        return Response({
            "detail": "Hospital Consult System API root - TODO: expand."
        })


# TODO: implement additional API views

from rest_framework.response import Response
from rest_framework.views import APIView


class APIRootView(APIView):
    """API root endpoint for the Hospital Consult System.

    This view provides a basic entry point to the API, returning a
    simple JSON response with links to the main API endpoints.
    """

    def get(self, request):
        """Handles GET requests to the API root.

        Args:
            request: The Django HttpRequest object.

        Returns:
            A DRF Response object with API information.
        """
        return Response({
            "message": "Hospital Consult System API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/v1/auth/",
                "departments": "/api/v1/departments/",
                "patients": "/api/v1/patients/",
                "consults": "/api/v1/consults/",
            }
        })

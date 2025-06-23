from rest_framework import status, viewsets
from rest_framework.response import Response

from scores.services.dashboard_service import DashboardService


class DashboardViewSet(viewsets.ViewSet):
    """API endpoints that power the *dashboard* page."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = DashboardService()

    def summary(self, request):
        try:
            payload = self._service.summary()
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"success": False, "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

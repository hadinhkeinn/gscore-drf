from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse

from scores.serializers.student_score_report_serializer import ScoreReportSerializer
from scores.services.student_score_report_service import ScoreReportService

class ScoreReportView(viewsets.ViewSet):
    """
    API View to generate score level reports with statistics
    """
    def __init__(self, **kwargs):
        super(ScoreReportView, self).__init__(**kwargs)
        self.service = ScoreReportService()

    def get_report(self, request):
        """
        Generate score statistics report for all subjects
        Returns statistics for 4 score levels:
        - Excellent: >= 8 points
        - Good: >= 6 and < 8 points
        - Average: >= 4 and < 6 points
        - Below Average: < 4 points
        """
        try:
            response_data = self.service.generate_score_report()
            serializer = ScoreReportSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_subject_detail(self, request, subject):
        """
        Get detailed statistics for a specific subject
        """
        try:
            response_data = self.service.get_subject_detail(subject)
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def score_chart_data(self, request):
        """
        Function-based view to return chart-ready data for score statistics
        Optimized for frontend chart libraries
        """
        try:
            return JsonResponse(self.service.get_score_chart_data())

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

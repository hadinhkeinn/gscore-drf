from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from scores.services import TopStudentScoreService


class TopStudentsGroupAView(ViewSet):
    """
    API View to get top 10 students in Group A (Math, Physics, Chemistry)
    Students are ranked by their total score in these 3 subjects
    """

    def __init__(self, **kwargs):
        super(TopStudentsGroupAView, self).__init__(**kwargs)
        self.service = TopStudentScoreService()

    def get(self, request):
        """
        Get top 10 students in Group A subjects
        Query parameters:
        - limit: Number of students to return (default: 10, max: 50)
        - min_subjects: Minimum number of subjects student must have scores for (default: 2)
        """
        try:
            limit = int(request.GET.get('limit', 10))
            min_subjects = int(request.GET.get('min_subjects', 2))

            response_data = self.service.rank_group_a_students(limit, min_subjects)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

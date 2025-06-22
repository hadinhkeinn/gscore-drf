from rest_framework import viewsets

from scores.models import StudentScore
from scores.serializers import StudentScoreSerializer


class StudentScoreViewSet(viewsets.ModelViewSet):
    queryset = StudentScore.objects.all().order_by("r_number")
    serializer_class = StudentScoreSerializer

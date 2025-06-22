from django.urls import path, include
from rest_framework.routers import DefaultRouter

from scores.views import StudentScoreViewSet, ScoreReportView, TopStudentsGroupAView

router = DefaultRouter()
router.register(r"scores", StudentScoreViewSet, basename="studentscore")

urlpatterns = [
    path('score-report/', ScoreReportView.as_view({'get': 'get_report'}), name='score-report'),
    path('score-report/subject/<str:subject>/', ScoreReportView.as_view({'get': 'get_subject_detail'}), name='subject_detail'),

    # Chart data endpoint (optimized for frontend charts)
    path('score-report/chart-data/', ScoreReportView.as_view({'get': 'score_chart_data'}), name='chart_data'),

    path('top-students/group-a/', TopStudentsGroupAView.as_view({'get': 'get'}), name='top_students_group_a'),

    path("", include(router.urls)),
]

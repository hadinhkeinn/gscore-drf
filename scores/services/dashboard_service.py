from typing import Dict

from django.db.models import Avg, Count, Case, When, IntegerField, Q
from django.utils import timezone

from scores.models import StudentScore
from scores.services.student_score_report_service import ScoreReportService, SUBJECT_FIELDS


class DashboardService:
    """Service layer to calculate high-level metrics for the *dashboard* page."""

    def __init__(self):
        self._score_report_service = ScoreReportService()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def summary(self) -> Dict:
        """Return a dictionary with all statistics required by the dashboard."""

        aggregation: dict[str, any] = {"total_students": Count("r_number")}

        for field in SUBJECT_FIELDS:
            aggregation[f"avg_{field}"] = Avg(field)
            aggregation[f"{field}_excellent"] = Count(
                Case(When(**{f"{field}__gte": 8.0}, then=1), output_field=IntegerField())
            )
            aggregation[f"{field}_good"] = Count(
                Case(
                    When(Q(**{f"{field}__gte": 6.0}) & Q(**{f"{field}__lt": 8.0}), then=1),
                    output_field=IntegerField(),
                )
            )
            aggregation[f"{field}_average"] = Count(
                Case(
                    When(Q(**{f"{field}__gte": 4.0}) & Q(**{f"{field}__lt": 6.0}), then=1),
                    output_field=IntegerField(),
                )
            )
            aggregation[f"{field}_below"] = Count(
                Case(When(**{f"{field}__lt": 4.0}, then=1), output_field=IntegerField())
            )

        stats = StudentScore.objects.aggregate(**aggregation)

        total_students = stats["total_students"]

        avg_per_subject_clean = {
            subject: round(stats.get(f"avg_{subject}") or 0, 2) for subject in SUBJECT_FIELDS
        }

        overall_avg = round(sum(avg_per_subject_clean.values()) / len(SUBJECT_FIELDS), 2)

        distribution = {
            "excellent": sum(stats[f"{s}_excellent"] for s in SUBJECT_FIELDS),
            "good": sum(stats[f"{s}_good"] for s in SUBJECT_FIELDS),
            "average": sum(stats[f"{s}_average"] for s in SUBJECT_FIELDS),
            "below_average": sum(stats[f"{s}_below"] for s in SUBJECT_FIELDS),
        }

        return {
            "success": True,
            "data": {
                "total_students": total_students,
                "overall_average_score": overall_avg,
                "average_scores_per_subject": avg_per_subject_clean,
                "score_distribution": distribution,
                "generated_at": timezone.now().isoformat(),
            },
        }

from typing import List, Optional

from django.db.models import Q, F, Case, When, FloatField, IntegerField, Sum, Count, Min, Max, Avg
from django.db.models.functions import Coalesce

from scores.services.student_score_service import StudentScoreService

GROUP_A_SUBJECTS = ['math', 'physics', 'chemistry']

class TopStudentScoreService:
    def __init__(self):
        self.score_service = StudentScoreService()

    def rank_group_a_students(
        self,
        limit: int = 10,
        min_subjects: int = 2,
    ) -> dict:
        """Return ranking data and summary for Group A students.

        Optimized version using database aggregation to handle large datasets efficiently.
        """

        limit = min(limit, 50)

        # Use database-level aggregation to calculate totals and counts
        students_qs = (
            self.score_service
            .list_scores()
            .filter(
                Q(math__isnull=False)
                | Q(physics__isnull=False)
                | Q(chemistry__isnull=False)
            )
            .exclude(
                math__isnull=True,
                physics__isnull=True,
                chemistry__isnull=True,
            )
            .annotate(
                # Count non-null subjects
                subjects_count=Sum(
                    Case(
                        When(math__isnull=False, then=1),
                        default=0,
                        output_field=IntegerField()
                    ) +
                    Case(
                        When(physics__isnull=False, then=1),
                        default=0,
                        output_field=IntegerField()
                    ) +
                    Case(
                        When(chemistry__isnull=False, then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                # Calculate total score (sum of non-null values)
                total_score=Sum(
                    Coalesce('math', 0.0) +
                    Coalesce('physics', 0.0) +
                    Coalesce('chemistry', 0.0)
                ),
                # Calculate average score
                average_score=Case(
                    When(subjects_count__gt=0, then=F('total_score') / F('subjects_count')),
                    default=0.0,
                    output_field=FloatField()
                )
            )
            .filter(subjects_count__gte=min_subjects)  # Filter by minimum subjects
            .order_by('-total_score', '-average_score', '-subjects_count')  # Order by ranking criteria
            .values(
                'r_number', 'math', 'physics', 'chemistry', 'foreign_lang_code',
                'subjects_count', 'total_score', 'average_score'
            )[:limit]  # Limit results at database level
        )

        # Convert to list and add ranking
        top_students = []
        for i, student in enumerate(students_qs, 1):
            # Build subject scores dict
            subject_scores = {}
            if student['math'] is not None:
                subject_scores['math'] = student['math']
            if student['physics'] is not None:
                subject_scores['physics'] = student['physics']
            if student['chemistry'] is not None:
                subject_scores['chemistry'] = student['chemistry']

            top_students.append({
                'rank': i,
                'r_number': student['r_number'],
                'subject_scores': subject_scores,
                'total_score': round(student['total_score'], 2),
                'average_score': round(student['average_score'], 2),
                'subjects_count': student['subjects_count'],
                'foreign_lang_code': student['foreign_lang_code'] or ''
            })

        # Get summary statistics using a separate optimized query
        summary = self._calculate_group_a_summary_optimized(min_subjects, top_students)

        return {
            'success': True,
            'data': {
                'top_students': top_students,
                'summary': summary,
                'criteria': {
                    'group': 'A',
                    'subjects': ['Mathematics', 'Physics', 'Chemistry'],
                    'ranking_method': 'Total score in Group A subjects',
                    'minimum_subjects': min_subjects,
                    'limit': limit
                }
            }
        }

    def _calculate_group_a_summary_optimized(self, min_subjects: int, top_students: List[dict]) -> dict:
        """Calculate summary statistics using database aggregation for better performance."""
        
        # Get all students statistics with database aggregation
        all_students_stats = (
            self.score_service
            .list_scores()
            .filter(
                Q(math__isnull=False)
                | Q(physics__isnull=False)
                | Q(chemistry__isnull=False)
            )
            .exclude(
                math__isnull=True,
                physics__isnull=True,
                chemistry__isnull=True,
            )
            .annotate(
                subjects_count=Sum(
                    Case(When(math__isnull=False, then=1), default=0, output_field=IntegerField()) +
                    Case(When(physics__isnull=False, then=1), default=0, output_field=IntegerField()) +
                    Case(When(chemistry__isnull=False, then=1), default=0, output_field=IntegerField())
                ),
                total_score=Sum(
                    Coalesce('math', 0.0) +
                    Coalesce('physics', 0.0) +
                    Coalesce('chemistry', 0.0)
                ),
                average_score=Case(
                    When(subjects_count__gt=0, then=F('total_score') / F('subjects_count')),
                    default=0.0,
                    output_field=FloatField()
                )
            )
            .filter(subjects_count__gte=min_subjects)
            .aggregate(
                total_students=Count('r_number'),
                highest_total=Max('total_score'),
                lowest_total=Min('total_score'),
                average_total=Avg('total_score'),
                average_score_mean=Avg('average_score')
            )
        )

        # Calculate top students statistics from the already fetched data
        top_count = len(top_students)
        if top_students:
            top_total_scores = [s['total_score'] for s in top_students]
            top_average_scores = [s['average_score'] for s in top_students]
            top_students_stats = {
                'highest_total': max(top_total_scores),
                'lowest_total': min(top_total_scores),
                'average_total': round(sum(top_total_scores) / len(top_total_scores), 2),
                'average_score_mean': round(sum(top_average_scores) / len(top_average_scores), 2)
            }
        else:
            top_students_stats = {
                'highest_total': 0,
                'lowest_total': 0,
                'average_total': 0,
                'average_score_mean': 0
            }

        return {
            'total_group_a_students': all_students_stats['total_students'] or 0,
            'top_students_count': top_count,
            'all_students_stats': {
                'highest_total': round(all_students_stats['highest_total'] or 0, 2),
                'lowest_total': round(all_students_stats['lowest_total'] or 0, 2),
                'average_total': round(all_students_stats['average_total'] or 0, 2),
                'average_score_mean': round(all_students_stats['average_score_mean'] or 0, 2)
            },
            'top_students_stats': top_students_stats
        }

    def _calculate_group_a_summary(self, all_students, top_students):
        if not all_students:
            return {}
        total_students = len(all_students)
        top_count = len(top_students)
        all_total_scores = [s['total_score'] for s in all_students]
        all_average_scores = [s['average_score'] for s in all_students]
        top_total_scores = [s['total_score'] for s in top_students]
        top_average_scores = [s['average_score'] for s in top_students]
        return {
            'total_group_a_students': total_students,
            'top_students_count': top_count,
            'all_students_stats': {
                'highest_total': max(all_total_scores),
                'lowest_total': min(all_total_scores),
                'average_total': round(sum(all_total_scores) / len(all_total_scores), 2),
                'average_score_mean': round(sum(all_average_scores) / len(all_average_scores), 2)
            },
            'top_students_stats': {
                'highest_total': max(top_total_scores) if top_total_scores else 0,
                'lowest_total': min(top_total_scores) if top_total_scores else 0,
                'average_total': round(sum(top_total_scores) / len(top_total_scores), 2) if top_total_scores else 0,
                'average_score_mean': round(sum(top_average_scores) / len(top_average_scores), 2) if top_average_scores else 0
            }
        }
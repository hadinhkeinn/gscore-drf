from typing import List, Optional

from django.db.models import Q

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

        The function now relies on :class:`StudentScoreService` for data access so
        we keep persistence concerns in a single place. A *service* instance can
        optionally be injected (useful for testing); otherwise, a new one will be
        created lazily.
        """

        limit = min(limit, 50)


        # Pull data via the service and apply the *Group A* filters.
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
        )

        student_rankings: List[dict] = []

        for student in students_qs:
            scores = []
            subject_scores = {}
            if student.math is not None:
                scores.append(student.math)
                subject_scores['math'] = student.math
            if student.physics is not None:
                scores.append(student.physics)
                subject_scores['physics'] = student.physics
            if student.chemistry is not None:
                scores.append(student.chemistry)
                subject_scores['chemistry'] = student.chemistry

            if len(scores) >= min_subjects:
                total_score = sum(scores)
                average_score = total_score / len(scores)
                student_rankings.append({
                    'r_number': student.r_number,
                    'subject_scores': subject_scores,
                    'total_score': round(total_score, 2),
                    'average_score': round(average_score, 2),
                    'subjects_count': len(scores),
                    'foreign_lang_code': student.foreign_lang_code or ''
                })

        student_rankings.sort(key=lambda x: (-x['total_score'], -x['average_score'], -x['subjects_count']))

        top_students = student_rankings[:limit]
        for i, st in enumerate(top_students, 1):
            st['rank'] = i

        summary = self._calculate_group_a_summary(student_rankings, top_students)

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
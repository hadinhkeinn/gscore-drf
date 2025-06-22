from django.utils import timezone

from scores.services.student_score_service import StudentScoreService

SUBJECT_FIELDS = [
    'math', 'literature', 'foreign_lang', 'physics',
    'chemistry', 'biology', 'history', 'geography', 'civic_education'
]

SUBJECT_NAMES = {
    'math': 'Mathematics',
    'literature': 'Literature',
    'foreign_lang': 'Foreign Language',
    'physics': 'Physics',
    'chemistry': 'Chemistry',
    'biology': 'Biology',
    'history': 'History',
    'geography': 'Geography',
    'civic_education': 'Civic Education'
}

class ScoreReportService:
    def __init__(self):
        self.student_score_service = StudentScoreService()

    def _generate_summary_stats(self, report_data: list[dict]) -> dict:
        """Generate overall summary statistics for all subjects."""
        total_excellent = sum(subject['statistics']['excellent'] for subject in report_data)
        total_good = sum(subject['statistics']['good'] for subject in report_data)
        total_average = sum(subject['statistics']['average'] for subject in report_data)
        total_below_average = sum(subject['statistics']['below_average'] for subject in report_data)
        total_scores = sum(subject['statistics']['total_students'] for subject in report_data)

        return {
            'total_scores_analyzed': total_scores,
            'overall_distribution': {
                'excellent': total_excellent,
                'good': total_good,
                'average': total_average,
                'below_average': total_below_average
            },
            'percentages': {
                'excellent': round((total_excellent / total_scores * 100), 2) if total_scores else 0,
                'good': round((total_good / total_scores * 100), 2) if total_scores else 0,
                'average': round((total_average / total_scores * 100), 2) if total_scores else 0,
                'below_average': round((total_below_average / total_scores * 100), 2) if total_scores else 0
            }
        }

    def generate_score_report(self) -> dict:
        """Compute statistics for all subjects and return serialized-ready dict."""
        report_data: list[dict] = []


        for field in SUBJECT_FIELDS:
            subject_stats = self.student_score_service.score_level_counts(field)

            report_data.append({
                'subject': field,
                'subject_name': SUBJECT_NAMES[field],
                'statistics': {
                    'excellent': subject_stats['excellent'],
                    'good': subject_stats['good'],
                    'average': subject_stats['average'],
                    'below_average': subject_stats['below_average'],
                    'total_students': subject_stats['total_students']
                }
            })

        summary = self._generate_summary_stats(report_data)

        return {
            'success': True,
            'data': {
                'subjects': report_data,
                'summary': summary,
                'score_levels': {
                    'excellent': '≥ 8.0 points',
                    'good': '6.0 ≤ score < 8.0 points',
                    'average': '4.0 ≤ score < 6.0 points',
                    'below_average': '< 4.0 points'
                }
            }
        }

    def get_subject_detail(self, subject: str) -> dict:
        """Return detailed statistics for a given subject."""
        if subject not in SUBJECT_FIELDS:
            raise ValueError(f'Invalid subject "{subject}"')

        scores = self.student_score_service.raw_scores(subject)
        if not scores:
            raise ValueError(f'No scores found for subject: {subject}')

        excellent = len([s for s in scores if s >= 8.0])
        good = len([s for s in scores if 6.0 <= s < 8.0])
        average = len([s for s in scores if 4.0 <= s < 6.0])
        below_average = len([s for s in scores if s < 4.0])

        total_students = len(scores)
        avg_score = sum(scores) / total_students

        return {
            'success': True,
            'data': {
                'subject': subject,
                'total_students': total_students,
                'score_distribution': {
                    'excellent': excellent,
                    'good': good,
                    'average': average,
                    'below_average': below_average
                },
                'percentages': {
                    'excellent': round((excellent / total_students * 100), 2),
                    'good': round((good / total_students * 100), 2),
                    'average': round((average / total_students * 100), 2),
                    'below_average': round((below_average / total_students * 100), 2)
                },
                'statistics': {
                    'average_score': round(avg_score, 2),
                    'highest_score': max(scores),
                    'lowest_score': min(scores)
                }
            }
        }

    def get_score_chart_data(self) -> dict:
        """Return chart ready data structure for score statistics."""
        chart_data = {
            'labels': [SUBJECT_NAMES[f] for f in SUBJECT_FIELDS],
            'datasets': [
                {
                    'label': 'Excellent (≥8)',
                    'data': [],
                    'backgroundColor': '#10B981',
                    'borderColor': '#059669',
                    'borderWidth': 1
                },
                {
                    'label': 'Good (6-8)',
                    'data': [],
                    'backgroundColor': '#3B82F6',
                    'borderColor': '#2563EB',
                    'borderWidth': 1
                },
                {
                    'label': 'Average (4-6)',
                    'data': [],
                    'backgroundColor': '#F59E0B',
                    'borderColor': '#D97706',
                    'borderWidth': 1
                },
                {
                    'label': 'Below Average (<4)',
                    'data': [],
                    'backgroundColor': '#EF4444',
                    'borderColor': '#DC2626',
                    'borderWidth': 1
                }
            ]
        }


        for field in SUBJECT_FIELDS:
            stats = self.student_score_service.score_level_counts(field)
            chart_data['datasets'][0]['data'].append(stats['excellent'])
            chart_data['datasets'][1]['data'].append(stats['good'])
            chart_data['datasets'][2]['data'].append(stats['average'])
            chart_data['datasets'][3]['data'].append(stats['below_average'])

        return {
            'success': True,
            'chartData': chart_data,
            'metadata': {
                'total_subjects': len(SUBJECT_FIELDS),
                'score_levels': 4,
                'generated_at': timezone.now().isoformat()
            }
        }
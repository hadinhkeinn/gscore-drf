from __future__ import annotations

from typing import Optional, Dict, Any

from scores.models import StudentScore


class StudentScoreRepository:
    def __init__(self):
        self.model = StudentScore

    # ---------------------------------------------------------------------
    # READ operations
    # ---------------------------------------------------------------------
    def list_all(self):
        """Return a *queryset* with **all** ``StudentScore`` rows."""
        return self.model.objects.all()

    def get_by_sbd(self, sbd: str):
        """Return a single object by its primary-key or *None* if not found."""
        try:
            return self.model.objects.get(r_number=sbd)
        except self.model.DoesNotExist:
            return None

    # New aggregation helpers ---------------------------------------------
    def aggregate_score_levels(self, subject: str) -> Dict[str, int]:
        """Return counts of score levels for *subject* (non-null rows only)."""
        from django.db.models import Count, Case, When, IntegerField, Q
        qs = self.model.objects.filter(**{f"{subject}__isnull": False})
        return qs.aggregate(
            excellent=Count(Case(When(**{f"{subject}__gte": 8.0}, then=1), output_field=IntegerField())),
            good=Count(Case(When(Q(**{f"{subject}__gte": 6.0}) & Q(**{f"{subject}__lt": 8.0}), then=1), output_field=IntegerField())),
            average=Count(Case(When(Q(**{f"{subject}__gte": 4.0}) & Q(**{f"{subject}__lt": 6.0}), then=1), output_field=IntegerField())),
            below_average=Count(Case(When(**{f"{subject}__lt": 4.0}, then=1), output_field=IntegerField())),
            total_students=Count(subject)
        )

    def list_scores_for_subject(self, subject: str):
        """Return a list of raw float scores for *subject* (non-null)."""
        return list(
            self.model.objects.filter(**{f"{subject}__isnull": False}).values_list(subject, flat=True)
        )

    # ---------------------------------------------------------------------
    # WRITE operations
    # ---------------------------------------------------------------------
    def create(self, **data: Any) -> StudentScore:
        """Insert a new row and return the created :class:`StudentScore`."""
        return self.model.objects.create(**data)

    def update(self, instance: StudentScore, **data: Any) -> StudentScore:
        """Update *``instance``* in-place with *data* and **persist** it."""
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save(update_fields=list(data.keys()) or None)
        return instance

    def delete(self, instance: StudentScore) -> None:
        """Delete *``instance``* from the database."""
        instance.delete()
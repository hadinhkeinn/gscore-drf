from __future__ import annotations

from typing import Any, Dict, Optional

from rest_framework.exceptions import NotFound

from scores.models import StudentScore
from scores.repositories import StudentScoreRepository


class StudentScoreService:
    """Business-logic layer for *student scores*.

    The service orchestrates application logic and delegates persistence to the
    :class:`StudentScoreRepository`.
    """
    def __init__(self):
        self.repo = StudentScoreRepository()

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def list_scores(self):
        return self.repo.list_all()

    def retrieve(self, sbd: str) -> StudentScore:
        student = self.repo.get_by_sbd(sbd)
        if student is None:
            raise NotFound(detail=f"StudentScore with id={sbd} not found")
        return student

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------
    def create(self, data: Dict[str, Any]) -> StudentScore:
        return self.repo.create(**data)

    def update(self, sbd: str, data: Dict[str, Any]) -> StudentScore:
        instance = self.retrieve(sbd)
        return self.repo.update(instance, **data)

    def delete(self, sbd: str) -> None:
        instance = self.retrieve(sbd)
        self.repo.delete(instance)

    # New reuse helpers ------------------------------------------------
    def score_level_counts(self, subject: str):
        """Wrapper for repository.aggregate_score_levels."""
        return self.repo.aggregate_score_levels(subject)

    def raw_scores(self, subject: str):
        """Return list[float] of scores for *subject* (non-null)."""
        return self.repo.list_scores_for_subject(subject)
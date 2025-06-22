from rest_framework import serializers

from scores.models import StudentScore


class StudentScoreSerializer(serializers.ModelSerializer):
    """Serializer for the :class:`~myapp.scores.models.StudentScore` model."""

    class Meta:
        model = StudentScore
        fields = "__all__"
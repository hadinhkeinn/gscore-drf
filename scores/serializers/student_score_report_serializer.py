from rest_framework import serializers


class ScoreLevelSerializer(serializers.Serializer):
    excellent = serializers.IntegerField()
    good = serializers.IntegerField()
    average = serializers.IntegerField()
    below_average = serializers.IntegerField()


class SubjectStatisticsSerializer(serializers.Serializer):
    excellent = serializers.IntegerField()
    good = serializers.IntegerField()
    average = serializers.IntegerField()
    below_average = serializers.IntegerField()
    total_students = serializers.IntegerField()


class SubjectReportSerializer(serializers.Serializer):
    subject = serializers.CharField()
    subject_name = serializers.CharField()
    statistics = SubjectStatisticsSerializer()


class SummaryStatisticsSerializer(serializers.Serializer):
    total_scores_analyzed = serializers.IntegerField()
    overall_distribution = ScoreLevelSerializer()
    percentages = serializers.DictField(child=serializers.FloatField())


class ScoreReportDataSerializer(serializers.Serializer):
    subjects = SubjectReportSerializer(many=True)
    summary = SummaryStatisticsSerializer()
    score_levels = serializers.DictField(child=serializers.CharField())


class ScoreReportSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = ScoreReportDataSerializer(required=False)
    error = serializers.CharField(required=False)
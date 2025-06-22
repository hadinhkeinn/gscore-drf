from django.db import models

class StudentScore(models.Model):
    r_number = models.CharField(primary_key=True, max_length=20)
    math = models.FloatField(null=True, blank=True)
    literature = models.FloatField(null=True, blank=True)
    foreign_lang = models.FloatField(null=True, blank=True)
    physics = models.FloatField(null=True, blank=True)
    chemistry = models.FloatField(null=True, blank=True)
    biology = models.FloatField(null=True, blank=True)
    history = models.FloatField(null=True, blank=True)
    geography = models.FloatField(null=True, blank=True)
    civic_education = models.FloatField(null=True, blank=True)
    foreign_lang_code = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.r_number



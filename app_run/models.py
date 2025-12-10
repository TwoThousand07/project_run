from django.db import models

from django.contrib.auth.models import User


class Run(models.Model):
    CHOICES = (
        ("init", "Инициализирован"),
        ("in_progress", "В процессе"),
        ("finished", "Завершенный")
    )

    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=CHOICES, default="init")

    def __str__(self):
        return f'{self.athlete.username}: {self.comment[:30]}'


class AthleteInfo(models.Model):
    athlete = models.OneToOneField(
        User, related_name="athlete_info", on_delete=models.CASCADE)

    goals = models.CharField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)


class Challenge(models.Model):
    full_name = models.CharField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.DecimalField(decimal_places=4, max_digits=7)
    longitude = models.DecimalField(decimal_places=4, max_digits=7)

from geopy.distance import geodesic

from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Run(models.Model):
    CHOICES = (
        ("init", "Инициализирован"),
        ("in_progress", "В процессе"),
        ("finished", "Завершенный")
    )

    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name="run")
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=CHOICES, default="init")

    distance = models.FloatField(default=0)

    run_time_seconds = models.IntegerField(default=0)

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

    def __str__(self):
        return f"{self.athlete.username} - {self.full_name}"


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.DecimalField(decimal_places=4, max_digits=7)
    longitude = models.DecimalField(decimal_places=4, max_digits=7)

    date_time = models.DateTimeField()

    def __str__(self):
        return f"{self.run.athlete.username} - latitude:{self.latitude}, longitude:{self.longitude}"

    def save(self, *args, **kwargs):

        items = CollectibleItem.objects.all()

        for item in items:
            if not (-90 <= item.latitude <= 90 and -180 <= item.longitude <= 180):
                continue

            distance = geodesic((item.latitude, item.longitude),
                                (self.latitude, self.longitude))

            if distance.m <= 100:
                self.run.athlete.items.add(item)
        super().save(*args, **kwargs)


class CollectibleItem(models.Model):
    name = models.CharField(max_length=128)
    uid = models.CharField(max_length=128, unique=True)
    value = models.IntegerField()
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)])
    picture = models.URLField()

    user_items = models.ManyToManyField(User, related_name="items", blank=True)

    def __str__(self):
        return f"{self.name} - ({self.latitude} : {self.longitude})"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

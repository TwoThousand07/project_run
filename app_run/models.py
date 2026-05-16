from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from geopy.distance import geodesic


class Run(models.Model):
    CHOICES = (
        ("init", "Инициализирован"),
        ("in_progress", "В процессе"),
        ("finished", "Завершенный"),
    )

    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name="run")
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=CHOICES, default="init")

    distance = models.FloatField(default=0)
    speed = models.FloatField(default=0, null=True)

    run_time_seconds = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.athlete.username}: {self.comment[:30]}"


class AthleteInfo(models.Model):
    athlete = models.OneToOneField(
        User, related_name="athlete_info", on_delete=models.CASCADE
    )

    goals = models.CharField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)


class Challenge(models.Model):
    full_name = models.CharField()
    athlete = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="challenges"
    )

    def __str__(self):
        return f"{self.athlete.username} - {self.full_name}"


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.DecimalField(decimal_places=4, max_digits=7)
    longitude = models.DecimalField(decimal_places=4, max_digits=7)

    date_time = models.DateTimeField()

    speed = models.FloatField(default=0)
    distance = models.FloatField(default=0)

    def __str__(self):
        return f"{self.run.athlete.username} - latitude:{self.latitude}, longitude:{self.longitude}"

    def save(self, *args, **kwargs):

        items = CollectibleItem.objects.all()

        for item in items:
            if not (-90 <= item.latitude <= 90 and -180 <= item.longitude <= 180):
                continue

            distance = geodesic(
                (item.latitude, item.longitude), (self.latitude, self.longitude)
            )

            if distance.m <= 100:
                self.run.athlete.items.add(item)
        super().save(*args, **kwargs)


class CollectibleItem(models.Model):
    name = models.CharField(max_length=128)
    uid = models.CharField(max_length=128, unique=True)
    value = models.IntegerField()
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    picture = models.URLField()

    user_items = models.ManyToManyField(User, related_name="items", blank=True)

    def __str__(self):
        return f"{self.name} - ({self.latitude} : {self.longitude})"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Subscripe(models.Model):
    coach = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers"
    )
    athlete = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )

    def __str__(self):
        return f"(({self.athlete.username})) subscribed to (({self.coach.username}))"

    class Meta:
        unique_together = ("coach", "athlete")


class Rating(models.Model):
    RATING_CHOICES = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]

    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")

    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.athlete.username} поставил тренеру {self.coach.username} рейтинг {self.rating}"

    class Meta:
        unique_together = ("coach", "athlete")

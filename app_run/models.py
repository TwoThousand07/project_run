from geopy.distance import geodesic

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

    distance = models.FloatField(default=0)

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

    def __str__(self):
        return f"{self.run.athlete.username} - latitude:{self.latitude}, longitude:{self.longitude}"

    def save(self, force_insert=..., force_update=..., using=..., update_fields=...):
        return super().save(force_insert, force_update, using, update_fields)
        
        items = CollectibleItem.objects.all()

        for item in items:
            distance = geodesic((item.latitude, item.longitude), (self.latitude, self.longitude))
            
            if distance.m <= 100:
                self.run.athlete.user_items.add(item)



class CollectibleItem(models.Model):
    name = models.CharField(max_length=128)
    uid = models.CharField(max_length=128, unique=True)
    value = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    picture = models.URLField()

    user_items = models.ManyToManyField(User, related_name="items")

    def __str__(self):
        return f"{self.name} - ({self.latitude} : {self.longitude})"

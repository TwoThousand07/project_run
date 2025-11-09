from django.db import models

from django.contrib.auth.models import User


# class User(AbstractUser):
#     CHOICES = (
#         ("athlete", "Атлет"),
#         ("coach", "Тренер")
#     )
    
#     type = models.CharField(max_length=20, choices=CHOICES, default="athlete")

#     def save(self, *args, **kwargs):
#         if self.type == "coach":
#             self.is_staff = True
#         super().save(*args, **kwargs)
    

class Run(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    
    def __str__(self):
        return f'{self.athlete.username}: {self.comment[:30]}'
    
    
from django.db import models

# Create your models here.
class User(models.Model):
    university_id = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.university_id
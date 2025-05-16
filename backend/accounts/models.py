from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    university_id = models.CharField(max_length=10, unique=True)
    university_password = models.CharField(max_length=20)
    
    def __str__(self):
        return self.username
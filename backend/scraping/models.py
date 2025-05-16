from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Assignment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    course_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title} - {self.course_name} ({self.due_date})"
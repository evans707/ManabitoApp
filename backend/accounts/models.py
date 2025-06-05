from django.db import models


class User(models.Model):
    university_id = models.CharField(max_length=10, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    logined_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.university_id
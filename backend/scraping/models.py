from django.db import models
from accounts.models import User


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True, help_text="課題ページのURLなどを保存") # URLを保存するために利用
    due_date = models.DateTimeField(null=True, blank=True) # 日付が取得できない場合も考慮
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        # userとtitleの組み合わせで同じ課題の重複登録を防ぐ
        unique_together = ('user', 'title')

    def __str__(self):
        return self.title
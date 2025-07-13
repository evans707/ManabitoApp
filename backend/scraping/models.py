from django.db import models
from accounts.models import User 

class Course(models.Model):
    # 曜日の選択肢を定義
    DAY_OF_WEEK_CHOICES = [
        (1, '月曜日'),
        (2, '火曜日'),
        (3, '水曜日'),
        (4, '木曜日'),
        (5, '金曜日'),
        (6, '土曜日'),
        (7, '日曜日'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=255, verbose_name='授業タイトル')
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES, verbose_name='曜日', null=True, blank=True)
    period = models.PositiveSmallIntegerField(verbose_name='時限', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    def __str__(self):
        return self.title

class Assignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments', null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name='課題タイトル')
    content = models.TextField(verbose_name='課題詳細', blank=True, null=True)
    url = models.URLField(max_length=512, verbose_name='課題URL', null=True, blank=True)
    start_date = models.DateTimeField(verbose_name='開始日時', null=True, blank=True)
    due_date = models.DateTimeField(verbose_name='提出期限', null=True, blank=True)
    is_submitted = models.BooleanField(default=False, verbose_name='提出済み')
    platform = models.CharField(max_length=255, verbose_name='プラットフォーム', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        unique_together = ('user', 'title', 'url')
        ordering = ['due_date']

    def __str__(self):
        return self.title
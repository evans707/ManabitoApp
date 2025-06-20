from rest_framework import serializers
from .models import Assignment


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'user', 'course', 'title', 'content', 'url', 'due_date', 'is_submitted']
        read_only_fields = ['id', 'user']
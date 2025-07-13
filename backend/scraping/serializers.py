from rest_framework import serializers
from .models import Assignment, Course


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'user', 'course', 'title', 'content', 'url', 'due_date', 'is_submitted']
        read_only_fields = ['id', 'user']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'user', 'title', 'day_of_week', 'period']
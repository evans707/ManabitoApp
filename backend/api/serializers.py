from rest_framework import serializers
from scraping.models import Assignment

# Serializer for the Assignment model
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
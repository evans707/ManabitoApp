from rest_framework import viewsets
from scraping.models import Assignment
from .serializers import AssignmentSerializer

# Create your views here.
class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

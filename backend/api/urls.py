from django.urls import path
from .views import Login
from .views import SampleAPIView

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('sample/', SampleAPIView.as_view(), name='sample'),
]
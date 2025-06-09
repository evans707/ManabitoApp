from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Login, SampleAPIView, LogoutView, AuthStatusView, CsrfTokenView, AssignmentViewSet

router = DefaultRouter()
router.register(r'assignments', AssignmentViewSet, basename='assignment')

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('sample/', SampleAPIView.as_view(), name='sample'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('auth/status/', AuthStatusView.as_view(), name='auth-status'),
    path('csrf/', CsrfTokenView.as_view(), name='csrf-token'),
    path('', include(router.urls))
]
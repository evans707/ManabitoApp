from django.urls import path
from .views import Login, SampleAPIView, LogoutView, AuthStatusView, CsrfTokenView

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('sample/', SampleAPIView.as_view(), name='sample'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('auth/status/', AuthStatusView.as_view(), name='auth-status'),
    path('csrf/', CsrfTokenView.as_view(), name='csrf-token'),
]
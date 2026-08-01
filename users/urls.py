from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ApproveVendorView,
    LoginView,
    MeView,
    PendingVendorListView,
    RegisterView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='auth-login-refresh'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('vendors/pending/', PendingVendorListView.as_view(), name='vendors-pending'),
    path('vendors/<int:pk>/approve/', ApproveVendorView.as_view(), name='vendor-approve'),
]

from django.urls import path

from .views import EsewaFailureView, EsewaVerifyView

urlpatterns = [
    path('esewa/verify/', EsewaVerifyView.as_view(), name='esewa-verify'),
    path('esewa/success/', EsewaVerifyView.as_view(), name='esewa-success'),
    path('esewa/failure/', EsewaFailureView.as_view(), name='esewa-failure'),
]

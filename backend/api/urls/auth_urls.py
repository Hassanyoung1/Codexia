# api/urls/auth_urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api.views.auth_views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    LogoutView,
    ResendOTPView,
    GoogleLoginView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
]
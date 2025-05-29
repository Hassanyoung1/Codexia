from django.urls import path
from api.views.auth_views import RegisterView, LoginView, LogoutView, PasswordResetView, GoogleAuthView, VerifyEmailView, PasswordResetConfirmView, VerifyOTPView
from django.urls import path


urlpatterns = [
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("reset-password/", PasswordResetView.as_view(), name="reset-password"),
    path("google-login/", GoogleAuthView.as_view(), name="google-login"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("reset-password-confirm/", PasswordResetConfirmView.as_view(), name="reset-password-confirm"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),  # ✅ New route for OTP verification
]

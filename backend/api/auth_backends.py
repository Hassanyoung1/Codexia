from django.contrib.auth.backends import ModelBackend
from api.models.user import User

class EmailBackend(ModelBackend):
    """
    Custom authentication backend to authenticate users with email instead of username.
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):  # 🔍 Check password
                return user
        except User.DoesNotExist:
            return None

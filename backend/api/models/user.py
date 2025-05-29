# File: /home/hassanyoung1/Focus-Reader/backend/api/models/user.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone
import jwt
from django.conf import settings
from datetime import timedelta, datetime
from django.utils.crypto import get_random_string
from django.utils.timezone import now  # Correct import for now

class BaseModel(models.Model):
    """Abstract base model to add timestamps for created and updated time."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This prevents Django from creating a separate table.


class UserManager(BaseUserManager):
    """
    Custom manager for User model that supports email-based authentication.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and returns a user with the given email and password.
        
        :param email: User's email (used as username)
        :param password: User's password
        :param extra_fields: Additional fields like first_name, last_name
        :return: User instance
        """
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with admin permissions.
        
        :param email: Admin email
        :param password: Admin password
        :param extra_fields: Additional fields
        :return: Superuser instance
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom User model that uses email instead of username.
    Supports Google OAuth and JWT authentication.
    """

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
   # email_verification_token = models.CharField(max_length=64, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    google_auth = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",  # ✅ Avoids conflicts
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # ✅ Avoids conflicts
        blank=True
    )


    def generate_email_verification_token(self):
        """Generates a random token for email verification."""
        self.email_verification_token = get_random_string(64)
        self.save()
        return self.email_verification_token


    def __str__(self):
        return self.email

    def get_full_name(self):
        """Returns the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Returns the short name of the user."""
        return self.first_name

    """ def generate_jwt_token(self):
        
        Generates a JSON Web Token (JWT) that expires in 7 days.

        :return: Encoded JWT token as a string.
        
        payload = {
            "user_id": self.id,
            "email": self.email,
            "exp": timezone.now() + timedelta(days=7),  # Token expires in 7 days
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256") """
    
    def generate_otp(self):
        """Generate and store OTP with an expiration time."""
        from django.utils.crypto import get_random_string

        self.otp = get_random_string(6, allowed_chars="0123456789")  # 6-digit OTP
        self.otp_expires_at = now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        self.save()
        return self.otp
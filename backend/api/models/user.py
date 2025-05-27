from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
from django.utils.crypto import get_random_string
from django.conf import settings

class UserManager(BaseUserManager):
    """
    Custom manager for User model that supports:
    - Email-based authentication
    - Superuser creation
    - OTP generation
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a User with the given email and password."""
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates and saves a superuser with admin permissions."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model supporting:
    - Email authentication (no username)
    - OTP verification
    - Google OAuth
    - JWT authentication
    """
    username = None
    email = models.EmailField(
        unique=True,
        db_index=True,
        validators=[EmailValidator()],
        help_text="Primary account identifier"
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="User's first name"
    )
    last_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="User's last name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether this user has verified their email"
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site"
    )
    google_auth = models.BooleanField(
        default=False,
        help_text="Designates whether this user authenticated via Google"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when user was created"
    )
    otp = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text="One-time password for verification"
    )
    otp_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Expiration time for OTP"
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Related names for auth models to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name="focusreader_users",
        blank=True,
        help_text="The groups this user belongs to",
        verbose_name="groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="focusreader_users",
        blank=True,
        help_text="Specific permissions for this user",
        verbose_name="user permissions"
    )

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Returns the user's short name (first name)."""
        return self.first_name

    def generate_otp(self):
        """
        Generates and stores a 6-digit OTP valid for 15 minutes.
        
        Example:
        >>> user = User.objects.get(email='test@example.com')
        >>> otp = user.generate_otp()
        >>> len(otp)
        6
        """
        self.otp = get_random_string(6, '0123456789')
        self.otp_expires_at = timezone.now() + timezone.timedelta(minutes=15)
        self.save()
        return self.otp

    def verify_otp(self, otp):
        """
        Verifies if the provided OTP is valid and not expired.
        
        Example:
        >>> user = User.objects.get(email='test@example.com')
        >>> user.verify_otp('123456')
        True
        """
        return (
            self.otp == otp and 
            self.otp_expires_at and 
            self.otp_expires_at > timezone.now()
        )

class OTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otp_entries"  # Avoid conflict with 'otp' in User model
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    class Meta:
        ordering = ['-created_at']
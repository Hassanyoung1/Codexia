# api/serializers/auth_serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from api.models.user import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta

class UserPublicSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for public representation.
    
    Example Response:
    {
        "id": 123,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = fields

class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for User Groups with permission details.
    
    Example Response:
    {
        "id": 1,
        "name": "Readers",
        "permissions": ["add_book", "view_book"]
    }
    """
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']
        read_only_fields = fields

    def get_permissions(self, obj):
        return [p.codename for p in obj.permissions.all()]

class UserSerializer(serializers.ModelSerializer):
    """
    Complete User serializer with security considerations.
    
    Example Response:
    {
        "id": 123,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_verified": true,
        "groups": [{"id": 1, "name": "Readers"}],
        "date_joined": "2023-01-15T10:30:00Z"
    }
    """
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'is_verified', 'groups', 'date_joined'
        ]
        read_only_fields = ['id', 'is_verified', 'date_joined']
        extra_kwargs = {
            'email': {
                'validators': [validate_email],
                'error_messages': {
                    'required': 'Email is required',
                    'invalid': 'Enter a valid email address',
                    'unique': 'This email is already registered'
                }
            },
            'first_name': {
                'max_length': 30,
                'error_messages': {
                    'max_length': 'First name cannot exceed 30 characters'
                }
            },
            'last_name': {
                'max_length': 30,
                'required': False,
                'error_messages': {
                    'max_length': 'Last name cannot exceed 30 characters'
                }
            }
        }

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address")
        return value.lower()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Secure user registration serializer with comprehensive validation.
    
    Example Request:
    {
        "email": "new@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!"
    }
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'},
        help_text="Minimum 8 characters with mix of letters and numbers"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Must match the password field"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        return data

    def validate_password(self, value):
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit"
            )
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        if not any(c.islower() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter"
            )
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    """
    Authentication serializer with JWT token generation.
    
    Example Request:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    
    Example Response:
    {
        "user": {
            "id": 123,
            "email": "user@example.com"
        },
        "tokens": {
            "refresh": "abc123...",
            "access": "xyz456..."
        }
    }
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address'
        }
    )
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True,
        error_messages={
            'required': 'Password is required'
        }
    )
    tokens = serializers.SerializerMethodField(read_only=True)

    def get_tokens(self, obj):
        user = obj['user']
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError({
                'non_field_errors': ['Both email and password are required']
            })
        
        user = authenticate(
            request=self.context.get('request'),
            email=email.lower(),
            password=password
        )
        
        if not user:
            raise serializers.ValidationError({
                'non_field_errors': ['Invalid email or password']
            })
        
        if not user.is_active:
            raise serializers.ValidationError({
                'non_field_errors': ['Account is disabled']
            })
            
        if not user.is_verified:
            raise serializers.ValidationError({
                'non_field_errors': ['Email not verified. Please check your inbox.']
            })
        
        data['user'] = user
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset requests.
    
    Example Request:
    {
        "email": "user@example.com"
    }
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address'
        }
    )

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value.lower())
            if not user.is_active:
                raise serializers.ValidationError("Account is disabled")
            return value.lower()
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email")

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    
    Example Request:
    {
        "token": "abc123...",
        "new_password": "NewSecurePass123!",
        "new_password_confirm": "NewSecurePass123!"
    }
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match'
            })
        return data

    def validate_new_password(self, value):
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit"
            )
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        return value

class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification requests.
    
    Example Request:
    {
        "token": "abc123..."
    }
    """
    token = serializers.CharField(required=True)

class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer for resending verification emails.
    
    Example Request:
    {
        "email": "user@example.com"
    }
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address'
        }
    )

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value.lower())
            if user.is_verified:
                raise serializers.ValidationError("Email is already verified")
            return value.lower()
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email")

class OTPSerializer(serializers.Serializer):
    """
    Serializer for OTP verification.
    
    Example Request:
    {
        "email": "user@example.com",
        "otp": "123456"
    }
    """
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        error_messages={
            'min_length': 'OTP must be 6 digits',
            'max_length': 'OTP must be 6 digits'
        }
    )

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'].lower())
            if user.otp != data['otp']:
                raise serializers.ValidationError({
                    'otp': 'Invalid OTP code'
                })
            if user.otp_expires_at < now():
                raise serializers.ValidationError({
                    'otp': 'OTP has expired'
                })
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No account found with this email'
            })
        

from django.contrib.auth import authenticate
from rest_framework import serializers
from api.models.user import User
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Example:
    >>> user = User(email="test@example.com", first_name="John", last_name="Doe")
    >>> serializer = UserSerializer(user)
    >>> serializer.data["email"]
    'test@example.com'
    """
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Example:
    >>> data = {"email": "test@example.com", "first_name": "John", "last_name": "Doe", "password": "securepass"}
    >>> serializer = RegisterSerializer(data=data)
    >>> serializer.is_valid()
    True
    """
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password")

    def create(self, validated_data):
        """
        Creates a new user with an encrypted password.
        """
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Example:
    >>> data = {"email": "test@example.com", "password": "securepass"}
    >>> serializer = LoginSerializer(data=data)
    >>> serializer.is_valid()
    True
    """ 
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'")

        data['user'] = user
        return data
    

class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset request.

    Example:
    >>> data = {"email": "test@example.com"}
    >>> serializer = PasswordResetSerializer(data=data)
    >>> serializer.is_valid()
    True
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Checks if the email exists in the system.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value


class GoogleAuthSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth login.

    Example:
    >>> data = {"email": "test@example.com", "first_name": "John", "last_name": "Doe", "google_auth": True}
    >>> serializer = GoogleAuthSerializer(data=data)
    >>> serializer.is_valid()
    True
    """
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    google_auth = serializers.BooleanField(default=True)

    def validate(self, data):
        """
        Creates or retrieves a Google-authenticated user and generates JWT tokens.
        """
        user, created = User.objects.get_or_create(email=data["email"], defaults=data)

        refresh = RefreshToken.for_user(user)
        return {
            "user": UserSerializer(user).data,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

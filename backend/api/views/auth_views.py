import os
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from google.auth.transport import requests
from google.oauth2 import id_token
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import AllowAny
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from core.utils import send_verification_email, send_password_reset_email, verify_password_reset_token, send_otp_email
from api.models.user import User
from rest_framework.generics import CreateAPIView
from django.http import JsonResponse
from api.serializers.auth_serializer import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    PasswordResetSerializer,
    GoogleAuthSerializer,
)
from django.http import JsonResponse
from datetime import timedelta, datetime
from django.utils.timezone import now  # ✅ Fix missing import


User = get_user_model()

User = get_user_model()


def welcome_view(request):
    """
    Returns a simple welcome message when accessing "/".
    """
    return JsonResponse({"message": "Welcome to the Codexia API!"})


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    **Example Usage (Doctest):**
    >>> from rest_framework.test import APIClient
    >>> client = APIClient()
    >>> response = client.post("/api/auth/signup/", {
    ...     "email": "test@example.com",
    ...     "first_name": "John",
    ...     "last_name": "Doe",
    ...     "password": "securepass123"
    ... }, format="json")
    >>> response.status_code
    201
    >>> "access_token" in response.data
    True
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


    def post(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                otp = user.generate_otp()
                send_otp_email(user.email, otp)
                
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "status": "success",
                        "message": "OTP sent for verification",
                        "data": {
                            "access_token": str(refresh.access_token),
                            "refresh_token": str(refresh),
                        }
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {
                    "status": "error",
                    "errors": serializer.errors,
                    "message": "Registration failed"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    
class LoginView(APIView):
    """
    API endpoint for user login.

    **Example Usage (Doctest):**
    >>> from rest_framework.test import APIClient
    >>> client = APIClient()
    >>> response = client.post("/api/auth/login/", {
    ...     "email": "test@example.com",
    ...     "password": "securepass123"
    ... }, format="json")
    >>> response.status_code
    200
    >>> "access_token" in response.data
    True
    """

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "message": "Login successful",
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh),
                    },
                    status=status.HTTP_200_OK,
                )
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        print(f"Login error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
    


class LogoutView(APIView):
    """
    API endpoint for user logout.

    **Example Usage (Doctest):**
    >>> from rest_framework.test import APIClient
    >>> client = APIClient()
    >>> response = client.post("/api/auth/logout/", {"refresh_token": "your_refresh_token"}, format="json")
    >>> response.status_code
    200
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    """
    API endpoint to request password reset.

    **Example Usage (Doctest):**
    >>> from rest_framework.test import APIClient
    >>> client = APIClient()
    >>> response = client.post("/api/auth/reset-password/", {"email": "test@example.com"}, format="json")
    >>> response.status_code
    200
    >>> response.data["message"]
    'Password reset link sent'
    """

    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = get_object_or_404(User, email=email)
            send_password_reset_email(user)  # ✅ Send password reset email, not verification email
            return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.utils.crypto import get_random_string

class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            google_client_id = os.getenv("GOOGLE_CLIENT_ID")
            id_info = id_token.verify_oauth2_token(token, requests.Request(), google_client_id)

            email = id_info.get("email")
            full_name = id_info.get("name", "")
            email_verified = id_info.get("email_verified")
            picture = id_info.get("picture")

            if not email or not email_verified:
                return Response({"error": "Email missing or not verified"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(email=email).first()

            if user:
                print(f"🔐 Logging in existing user: {user.email}")
            else:
                print(f"🆕 Registering new user for: {email}")

                # Generate safe, unique username
                username = self.generate_unique_username(email)

                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password=get_random_string(32),  # set a random password (not used)
                    first_name=full_name.split()[0] if full_name else "",
                    last_name=full_name.split()[-1] if full_name else "",
                    profile_image_url=picture,
                    is_verified=True,
                )

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login/signup successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        except ValueError as ve:
            print(f"❌ Token error: {ve}")
            return Response({"error": "Invalid Google token"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(f"🔥 Unexpected error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_unique_username(self, email: str) -> str:
        base = email.split("@")[0]
        username = base
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        return username

class VerifyEmailView(APIView):
    """
    API endpoint to verify email from the token.
    """
    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 🔍 Debugging print
        print(f"🔍 Received Token: {token}")

        # 🛠 Fix: Query the user correctly
        try:
            user = User.objects.get(email_verification_token=token)  # ✅ Make sure this works
        except User.DoesNotExist:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.email_verification_token = None  # ✅ Clear token after verification
        user.save()

        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
    
# File: backend/api/views/auth_views.py

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is missing'}, status=400)

        try:
            email = verify_password_reset_token(token)
            print(f"Extracted email from token: {email}")  # Debugging line
        except Exception as e:
            return Response({'error': f'Invalid token: {str(e)}'}, status=400)

        # Assuming the new password is sent in the request body
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'New password is missing'}, status=400)

        try:
            user = User.objects.get(email=email)
            print(f"User found: {user.email}")  # Debugging line
            user.set_password(new_password)  # Ensure password is hashed
            user.save()
            return Response({'success': 'Password has been reset successfully'}, status=200)
        except User.DoesNotExist:
            print(f"User with email {email} not found")  # Debugging line
            return Response({'error': 'User not found'}, status=400)




class VerifyOTPView(APIView):
    """
    API endpoint to verify OTP.
    **Example Usage (Doctest):**
    >>> from rest_framework.test import APIClient
    >>> client = APIClient()
    >>> response = client.post("/api/auth/verify-otp/", {"email": "test@example.com", "otp": "123456"}, format="json")
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, email=email)

        # Check if OTP is valid and not expired
        if user.otp == otp and user.otp_expires_at and user.otp_expires_at > now():
            user.is_verified = True  # ✅ Mark user as verified
            user.otp = None  # ✅ Clear OTP after successful verification
            user.otp_expires_at = None
            user.save()
            return Response({"message": "OTP verified successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

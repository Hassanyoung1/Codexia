# api/views/auth_views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from api.serializers.auth_serializer import (
    RegisterSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer
)

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from api.models.user import  User, OTP
import random

from django.http import JsonResponse
from datetime import timedelta
from django.utils.timezone import now

# api/views/auth_views.py
from google.oauth2 import id_token
from google.auth.transport import requests

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=idinfo['email'],
                defaults={
                    'first_name': idinfo.get('given_name', ''),
                    'last_name': idinfo.get('family_name', ''),
                    'is_active': True
                }
            )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name
                }
            })
            
        except ValueError:
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


def welcome_view(request):
    return JsonResponse({"message": "Welcome to Focus Reader!"})


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration with email verification.
    
    POST /auth/register/
    {
        "email": "user@example.com",
        "password": "securepass123",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user but keep inactive until verified
        user = serializer.save(is_active=False)
        
        # Generate and send OTP
        otp = random.randint(100000, 999999)
        OTP.objects.create(
            user=user,
            code=otp,
            expires_at=now() + timedelta(minutes=5)  # Set expiration time to 5 minutes from now
)
        
        send_mail(
            'Verify your FocusReader account',
            f'Your verification code is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return Response(
            {
                'detail': 'Verification code sent to email',
                'user_id': user.id,
            },
            status=status.HTTP_201_CREATED
        )

class VerifyEmailView(APIView):
    """
    API endpoint for email verification with OTP.
    
    POST /auth/verify-email/
    {
        "user_id": 1,
        "code": "123456"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(id=serializer.validated_data['user_id'])
        otp = OTP.objects.filter(
            user=user,
            code=serializer.validated_data['code']
        ).first()
        
        if not otp or otp.is_expired():
            return Response(
                {'detail': 'Invalid or expired code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Activate user and clean up OTP
        user.is_active = True
        user.save()
        otp.delete()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name
            }
        })

class LoginView(APIView):
    """
    API endpoint for user authentication.
    
    POST /auth/login/
    {
        "email": "user@example.com",
        "password": "securepass123"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'detail': 'Account not activated'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name
            }
        })

class PasswordResetRequestView(APIView):
    """
    API endpoint for password reset requests.
    
    POST /auth/password-reset/
    {
        "email": "user@example.com"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(email=serializer.validated_data['email'])
        
        # Generate and send reset token (in production, use a secure token generator)
        reset_token = RefreshToken.for_user(user).access_token
        
        send_mail(
            'Password Reset Request',
            f'Use this token to reset your password: {reset_token}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return Response(
            {'detail': 'Password reset email sent'},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(APIView):
    """
    API endpoint for password reset confirmation.
    
    POST /auth/password-reset-confirm/
    {
        "token": "abc123",
        "new_password": "newsecure123"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In production, verify the token properly
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'detail': 'Password updated successfully'},
            status=status.HTTP_200_OK
        )

class LogoutView(APIView):
    """
    API endpoint for user logout (token blacklisting).
    
    POST /auth/logout/
    {
        "refresh": "refresh_token"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'detail': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ResendOTPView(APIView):
    """
    API endpoint for resending OTP codes.
    
    POST /auth/resend-otp/
    {
        "email": "user@example.com"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            user = User.objects.get(email=request.data.get('email'))
            if user.is_active:
                return Response(
                    {'detail': 'Account already activated'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Delete any existing OTPs
            OTP.objects.filter(user=user).delete()
            
            # Generate and send new OTP
            otp = random.randint(100000, 999999)
            OTP.objects.create(user=user, code=otp)
            
            send_mail(
                'Your new verification code',
                f'Your new code is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return Response(
                {'detail': 'New verification code sent'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
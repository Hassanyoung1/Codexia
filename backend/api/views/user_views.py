# api/views/user_views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models.user import User
from api.serializers.auth_serializer import (
    UserSerializer,
    PasswordResetRequestSerializer,
    EmailVerificationSerializer
)
from django.contrib.auth import update_session_auth_hash

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user profile management.
    
    Supported Actions:
    - Get profile (GET /profile/)
    - Update profile (PATCH /profile/)
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class PasswordChangeView(generics.GenericAPIView):
    """
    API endpoint for password changes.
    
    Supported Actions:
    - Change password (POST /profile/password/)
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.data.get('old_password')):
            return Response(
                {'old_password': 'Incorrect password'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.set_password(serializer.data.get('new_password'))
        user.save()
        
        # Maintain session after password change
        update_session_auth_hash(request, user)
        
        return Response({'status': 'password changed'})

class EmailUpdateView(generics.GenericAPIView):
    """
    API endpoint for email updates.
    
    Supported Actions:
    - Request email change (POST /profile/email/)
    - Verify new email (POST /profile/email/verify/)
    """
    serializer_class = EmailVerificationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # In a real implementation, you would send verification email
        request.user.email = serializer.validated_data['new_email']
        request.user.is_verified = False
        request.user.save()
        
        return Response({
            'status': 'verification_email_sent',
            'email': request.user.email
        })
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now, timedelta
from api.models.focus import ReadingSession, BlockedApp, BlockedWebsite
from api.serializers.focus_serializer import ReadingSessionSerializer, BlockedAppSerializer, BlockedWebsiteSerializer
from django.contrib.auth import get_user_model
from services.blocking import BlockingService

class ReadingSessionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def start_reading(self, request):
        """Start a new reading session & enforce blocking."""
        if ReadingSession.objects.filter(user=request.user, completed=False).exists():
                    return Response(
                        {"error": {"code": 400, "message": "Active session exists"}},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        serializer = ReadingSessionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                 {"error": {"code": 400, "errors": serializer.errors}},
                 status=status.HTTP_400_BAD_REQUEST
                 )

        session = serializer.save(user=request.user)
        blocking_config = BlockingService.enforce(
             user=request.user,
             hard_lock=serializer.validated_data.get("hard_lock", False)
             )
        return Response({
             "session": ReadingSessionSerializer(session).data,
             "blocking_config": blocking_config
             }, status=status.HTTP_201_CREATED)
    

    def end_reading(self, request):
        """End an active reading session & restore access."""
        session = ReadingSession.objects.filter(user=request.user, completed=False).last()

        if not session:
            return Response({"error": "No active reading session found."}, status=status.HTTP_400_BAD_REQUEST)

        if "confirm" not in request.data or request.data["confirm"] is not True:
            return Response({"error": "Confirmation required to end the session."}, status=status.HTTP_400_BAD_REQUEST)

        session.end_session()
        self.restore_access(request.user)
        return Response(ReadingSessionSerializer(session).data, status=status.HTTP_200_OK)

    def enforce_blocking(self, user):
        """Block all apps except messaging and phonebook apps."""
        allowed_apps = {"com.android.mms", "com.android.contacts"}  # Messages & Phonebook

        # Block all apps stored in the database except allowed ones
        blocked_apps = BlockedApp.objects.filter(user=user).exclude(package_name__in=allowed_apps)

        for app in blocked_apps:
            print(f"Blocking app: {app.app_name} ({app.package_name})")  # Simulate blocking


    def restore_access(self, user):
        """Restore access after a reading session ends."""
        user_identifier = getattr(user, "username", None) or getattr(user, "email", "Unknown User")
        print(f"Restoring access for user: {user_identifier}")


    def reading_stats(self, request):
        """Return reading stats for the user."""
        sessions = ReadingSession.objects.filter(user=request.user)
        serializer = ReadingSessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def enforce_hard_lock(self, user):
        """Simulate hard lock by restricting access to other apps completely."""
        print(f"🔒 Enforcing HARD LOCK for user: {user}")
    # TODO: Implement hard lock logic in mobile/web app


# 🚀 API Views for managing Blocked Apps & Websites
class BlockingViewSet(viewsets.ViewSet):
    """Handles app and website blocking."""
    permission_classes = [IsAuthenticated]

    """def activate_blocking(self, request):
        Activate blocking of specified apps and websites.
        self.enforce_blocking(request.user)
        return Response({"message": "Blocking activated"}, status=status.HTTP_200_OK)"""
    
    def activate_blocking(self, request):
        """Activate blocking of specified apps and websites."""
        config = BlockingService.enforce(request.user)
        return Response({"message": "Blocking activated", "config": config}, status=status.HTTP_200_OK)
    
    def restore_access(self, user):
         user_identifier = getattr(user, "username", None) or getattr(user, "email", "Unknown User")
         print(f"Restoring access for user: {user_identifier}")

    def deactivate_blocking(self, request):
        """Deactivate blocking and restore access."""
        self.restore_access(request.user)
        return Response({"message": "Blocking deactivated"}, status=status.HTTP_200_OK)

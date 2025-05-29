from rest_framework import generics, permissions
from api.models.badge import Badge, UserBadge
from api.serializers.badge_serializer import BadgeSerializer, UserBadgeSerializer

class BadgeListView(generics.ListAPIView):
    """
    API to fetch all available badges.
    """
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.AllowAny]


class UserBadgeListView(generics.ListAPIView):
    """
    API to fetch all badges earned by the user.
    """
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user)

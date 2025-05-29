from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.focus import BlockedApp, BlockedWebsite
from api.serializers.focus_serializer import BlockedAppSerializer, BlockedWebsiteSerializer

class BlockedAppViewSet(viewsets.ModelViewSet):
    """Manage blocked apps"""
    serializer_class = BlockedAppSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BlockedApp.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BlockedWebsiteViewSet(viewsets.ModelViewSet):
    """Manage blocked websites"""
    serializer_class = BlockedWebsiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BlockedWebsite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

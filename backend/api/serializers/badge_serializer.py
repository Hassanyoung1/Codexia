from rest_framework import serializers
from api.models.badge import Badge, UserBadge

class BadgeSerializer(serializers.ModelSerializer):
    """
    Serializer for Badge model.
    """

    class Meta:
        model = Badge
        fields = ["id", "name", "description", "streak_required", "image_url"]


class UserBadgeSerializer(serializers.ModelSerializer):
    """
    Serializer for UserBadge model.
    """

    badge = BadgeSerializer()  # 🔥 Include badge details

    class Meta:
        model = UserBadge
        fields = ["id", "badge", "earned_at"]

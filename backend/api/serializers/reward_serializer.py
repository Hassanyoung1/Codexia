from rest_framework import serializers
from api.models.rewards import Reward, UserReward

class RewardSerializer(serializers.ModelSerializer):
    """
    Serializer for Reward model.
    """

    class Meta:
        model = Reward
        fields = ["id", "description", "reward_type", "discount_value", "free_book_id"]


class UserRewardSerializer(serializers.ModelSerializer):
    """
    Serializer for UserReward model.
    """

    reward = RewardSerializer()  # 🔥 Include reward details

    class Meta:
        model = UserReward
        fields = ["id", "reward", "redeemed", "earned_at"]

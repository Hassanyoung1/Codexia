from rest_framework import generics, permissions
from rest_framework.response import Response
from api.models.rewards import UserReward
from api.serializers.reward_serializer import UserRewardSerializer

class UserRewardListView(generics.ListAPIView):
    """
    API to fetch all rewards earned by the user.
    """
    serializer_class = UserRewardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserReward.objects.filter(user=self.request.user, redeemed=False)


class RedeemRewardView(generics.UpdateAPIView):
    """
    API to redeem a reward.
    """
    serializer_class = UserRewardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        reward = UserReward.objects.filter(user=request.user, pk=pk, redeemed=False).first()
        if not reward:
            return Response({"error": "Reward not found or already redeemed"}, status=400)

        reward.redeemed = True
        reward.save()

        return Response({"message": "Reward redeemed successfully!"}, status=200)

from django.db import models
from django.conf import settings

class Reward(models.Model):
    """
    Defines rewards that users can earn for achieving badges.
    """
    badge = models.OneToOneField("Badge", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    reward_type = models.CharField(
        max_length=50,
        choices=[("discount", "Discount"), ("free_book", "Free Book")],
    )
    discount_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # % discount
    free_book_id = models.PositiveIntegerField(null=True, blank=True)  # 🔥 ID of the free book

    def __str__(self):
        return f"Reward for {self.badge.name}"


class UserReward(models.Model):
    """
    Stores rewards earned by users.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    redeemed = models.BooleanField(default=False)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "reward")

    def __str__(self):
        return f"{self.user.email} - {self.reward.description}"

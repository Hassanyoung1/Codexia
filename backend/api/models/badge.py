from django.db import models
from django.conf import settings
from django.utils.timezone import now
from core.notifications import send_push_notification, send_email_notification
from api.models.rewards import Reward, UserReward

class Badge(models.Model):
    """
    Model to store available badges and their requirements.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    streak_required = models.PositiveIntegerField()  # 🔥 Number of days required to earn badge
    image_url = models.URLField(blank=True, null=True)  # 🔥 Optional badge image

    def __str__(self):
        return f"{self.name} - {self.streak_required} Days"


class UserBadge(models.Model):
    """
    Stores badges earned by users.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")  # 🔥 Prevents duplicate badges


   
    def save(self, *args, **kwargs):
        """
        Override save method to send notifications and assign rewards.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            message = f"🎉 Congratulations! You earned the '{self.badge.name}' badge!"
            send_push_notification(self.user, message)
            send_email_notification(self.user.email, "New Badge Earned!", message)

            # 🔥 Check if this badge unlocks a reward
            reward = Reward.objects.filter(badge=self.badge).first()
            if reward:
                UserReward.objects.create(user=self.user, reward=reward)
                send_push_notification(self.user, f"🎁 You unlocked a reward: {reward.description}!")


    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"

from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils.timezone import now, localtime
from api.models.badge import Badge, UserBadge

class ReadingGoal(models.Model):
    """
    Model to track user reading goals, progress, and streaks.
    """

    GOAL_TYPES = [
        ("pages", "Pages"),
        ("minutes", "Minutes"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=10, choices=GOAL_TYPES, default="pages")
    goal_target = models.PositiveIntegerField()
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    streak_count = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)  # 🔥 NEW: Stores the longest streak
    last_completed_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def update_progress(self, amount):
        """
        Increases progress and checks if the goal is completed.
        """
        self.progress += amount
        if self.progress >= self.goal_target and not self.is_completed:
            self.complete_goal()
        self.save()

    def complete_goal(self):
        """
        Marks the goal as completed and updates the streak count.
        Also updates historical streak tracking.
        """
        today = localtime(now()).date()

        if self.is_completed:  
            return  

        if self.last_completed_date:
            difference = (today - self.last_completed_date).days
            if difference == 1:  
                self.streak_count += 1  # 🔥 Continue streak
            elif difference > 1:
                self.streak_count = 1  # 🔥 Reset streak if skipped a day
        else:
            self.streak_count = 1  # 🔥 First goal completion

        # 🔥 Track longest streak
        if self.streak_count > self.longest_streak:
            self.longest_streak = self.streak_count

        self.is_completed = True
        self.last_completed_date = today  

        # 🔥 Save history for tracking
        ReadingHistory.objects.create(user=self.user, date=today, streak_count=self.streak_count)

        self.save()

    def reset_goal(self):
        """
        Resets the goal for a new day.
        If the user missed a day, streak is reset.
        """
        today = localtime(now()).date()

        if self.last_completed_date and (today - self.last_completed_date).days > 1:
            self.streak_count = 0  

        self.progress = 0
        self.is_completed = False
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.goal_target} {self.goal_type} (Streak: {self.streak_count})"
    

    def check_for_badges(self):
        """
        Checks if user qualifies for a new badge and awards it.
        """
        eligible_badges = Badge.objects.filter(streak_required__lte=self.streak_count)
        for badge in eligible_badges:
            if not UserBadge.objects.filter(user=self.user, badge=badge).exists():
                UserBadge.objects.create(user=self.user, badge=badge)



class ReadingHistory(models.Model):
    """
    Stores daily reading streak records for analytics.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    streak_count = models.PositiveIntegerField()

    class Meta:
        unique_together = ("user", "date")  # 🔥 Prevents duplicate entries

    def __str__(self):
        return f"{self.user.email} - {self.date} (Streak: {self.streak_count})"

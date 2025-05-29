from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta

User = get_user_model()

class ReadingSession(models.Model): 
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_id = models.CharField(max_length=255)  # Track what book user is reading
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    reading_duration = models.PositiveIntegerField()  # Tracks reading duration
    completed = models.BooleanField(default=False)
    interruptions = models.PositiveIntegerField(default=0)
    focus_score = models.PositiveIntegerField(default=100)
    hard_lock = models.BooleanField(default=False) 


    def calculate_focus_score(self):
        """Calculate focus score based on reading session and interruptions."""
        if not self.end_time:
            return self.focus_score  

        time_spent = (self.end_time - self.start_time).total_seconds() / 60
        expected_time = self.reading_duration

        time_penalty = max(0, (expected_time - time_spent) / expected_time * 50)
        interruption_penalty = min(50, self.interruptions * 10)

        self.focus_score = max(0, 100 - (time_penalty + interruption_penalty))
        return self.focus_score

    def end_session(self):
        """Mark session as completed and calculate focus score."""
        if not self.end_time:
            self.end_time = now()

        expected_end_time = self.start_time + timedelta(minutes=self.reading_duration)
        if self.end_time < expected_end_time:
            self.end_time = expected_end_time

        self.completed = True
        self.calculate_focus_score()
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.book_id} - {self.reading_duration} min - Score: {self.focus_score}%"

class BlockedApp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app_name = models.CharField(max_length=100)
    package_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.app_name} ({self.package_name})"


class BlockedWebsite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.url}"


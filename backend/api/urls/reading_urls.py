# File: backend/api/urls/reading_urls.py

from django.urls import path
from api.views.reading_views import SetReadingGoalView, UpdateProgressView, GetReadingGoalView, GetReadingStreakView, WeeklyStreakView, MonthlyStreakView

urlpatterns = [
    path("goal/", SetReadingGoalView.as_view(), name="set_goal"),
    path("progress/", UpdateProgressView.as_view(), name="update_progress"),
    path("status/", GetReadingGoalView.as_view(), name="get_goal"),
    path("streaks/", GetReadingStreakView.as_view(), name="get_streak"),
    path("streaks/weekly/", WeeklyStreakView.as_view(), name="weekly_streaks"),
    path("streaks/monthly/", MonthlyStreakView.as_view(), name="monthly_streaks"),
]
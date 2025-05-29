from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models.reading import ReadingGoal, ReadingHistory
from api.serializers.reading_serializer import ReadingGoalSerializer
from django.utils import timezone
from django.utils.timezone import now, localtime
from datetime import timedelta

class SetReadingGoalView(generics.CreateAPIView):
    """
    API to create a new reading goal.
    Example:
        >>> client.post("/api/reading/goal/", {"goal_type": "pages", "goal_target": 20})
    """
    serializer_class = ReadingGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            goal, created = ReadingGoal.objects.update_or_create(
                user=request.user,
                defaults={
                    "goal_type": serializer.validated_data["goal_type"],
                    "goal_target": serializer.validated_data["goal_target"],
                    "progress": 0,
                    "is_completed": False,
                },
            )
            return Response(ReadingGoalSerializer(goal).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProgressView(APIView):
    """
    API to update reading progress.
    Example:
        >>> client.post("/api/reading/progress/", {"amount": 5})
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        goal = ReadingGoal.objects.filter(user=request.user).first()
        if not goal:
            return Response({"error": "No reading goal set"}, status=status.HTTP_400_BAD_REQUEST)

        amount = request.data.get("amount", 0)
        goal.update_progress(amount)

        return Response(ReadingGoalSerializer(goal).data, status=status.HTTP_200_OK)


class GetReadingGoalView(generics.RetrieveAPIView):
    """
    API to get the user's current reading goal.
    Example:
        >>> client.get("/api/reading/goal/")
    """
    serializer_class = ReadingGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return ReadingGoal.objects.filter(user=self.request.user).first()
    

class GetReadingStreakView(APIView):
    """
    API to get user's reading streak.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        goal = ReadingGoal.objects.filter(user=request.user).first()
        if not goal:
            return Response({"error": "No reading goal set"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "streak_count": goal.streak_count,
            "last_completed_date": goal.last_completed_date,
        }, status=status.HTTP_200_OK)


class WeeklyStreakView(APIView):
    """
    API to fetch weekly reading streak history.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = localtime(now()).date()
        week_start = today - timedelta(days=today.weekday())  # 🔥 Get Monday of this week
        week_data = ReadingHistory.objects.filter(user=request.user, date__gte=week_start)

        return Response({
            "weekly_streaks": [
                {"date": record.date, "streak_count": record.streak_count} for record in week_data
            ]
        }, status=200)


class MonthlyStreakView(APIView):
    """
    API to fetch monthly reading streak history.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = localtime(now()).date()
        month_start = today.replace(day=1)  # 🔥 Get 1st day of this month
        month_data = ReadingHistory.objects.filter(user=request.user, date__gte=month_start)

        return Response({
            "monthly_streaks": [
                {"date": record.date, "streak_count": record.streak_count} for record in month_data
            ]
        }, status=200)


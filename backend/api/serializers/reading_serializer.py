
from rest_framework import serializers
from api.models.reading import ReadingGoal

class ReadingGoalSerializer(serializers.ModelSerializer):
    """
    Serializer for ReadingGoal model with all fields included.
    """
    class Meta:
        model = ReadingGoal
        fields = [
            "id", 
            "user",
            "goal_type", 
            "goal_target", 
            "progress", 
            "is_completed", 
            "streak_count",
            "longest_streak",
            "last_completed_date",
            "created_at",
            "last_updated"
        ]
        read_only_fields = [
            "user",
            "is_completed", 
            "streak_count",
            "longest_streak",
            "last_completed_date",
            "created_at",
            "last_updated"
        ]

    def validate_goal_target(self, value):
        if value <= 0:
            raise serializers.ValidationError("Goal target must be positive")
        return value
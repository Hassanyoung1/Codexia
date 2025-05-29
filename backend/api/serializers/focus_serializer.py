from rest_framework import serializers
from api.models.focus import ReadingSession, BlockedApp, BlockedWebsite

class ReadingSessionSerializer(serializers.ModelSerializer):
    focus_score = serializers.SerializerMethodField()
    total_reading_time = serializers.SerializerMethodField()

    class Meta:
        model = ReadingSession
        fields = ["id", "user", "book_id", "start_time", "end_time", "reading_duration", "completed", "interruptions", "focus_score", "total_reading_time", "hard_lock"]
        read_only_fields = ["id", "start_time", "end_time", "completed", "focus_score", "total_reading_time"]

    def get_focus_score(self, obj):
        return obj.calculate_focus_score()

    def validate_reading_duration(self, value):
        """Ensure reading duration is reasonable."""
        if value < 5 or value > 180:
            raise serializers.ValidationError("Reading duration must be between 5 and 180 minutes.")
        return value
    
    def get_total_reading_time(self, obj):
        """Calculate actual reading time spent."""
        if obj.end_time:
            time_spent = (obj.end_time - obj.start_time).total_seconds() / 60
            return round(time_spent, 2)
        return 0

class BlockedAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedApp
        fields = ["id", "user", "app_name", "package_name", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

class BlockedWebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedWebsite
        fields = ["id", "user", "url", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

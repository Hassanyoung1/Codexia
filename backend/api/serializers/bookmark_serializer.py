from rest_framework import serializers
from api.models.bookmark import Bookmark, Highlight

class BookmarkSerializer(serializers.ModelSerializer):
    """
    Serializer for Bookmark model.
    """

    class Meta:
        model = Bookmark
        fields = ["id", "book", "page_number", "note", "created_at"]
        read_only_fields = ["user", "created_at"]


class HighlightSerializer(serializers.ModelSerializer):
    """
    Serializer for Highlight model.
    """

    class Meta:
        model = Highlight
        fields = ["id", "book", "page_number", "text", "created_at"]
        read_only_fields = ["user", "created_at"]

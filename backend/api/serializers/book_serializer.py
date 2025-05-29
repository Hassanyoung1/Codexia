from rest_framework import serializers
from api.models.book import Book, Category, Tag



class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """

    class Meta:
        model = Category
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    """

    class Meta:
        model = Tag
        fields = ["id", "name"]



class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model.
    """

    category = CategorySerializer(read_only=True)  # 🔥 Nested category details
    tags = TagSerializer(many=True, read_only=True)  

    class Meta:
        model = Book
        fields = ["id", "user", "title", "author", "file", "category", "tags", "uploaded_at"]
        read_only_fields = ["user", "uploaded_at"]

    def validate_author(self, value):
        """
        Ensure author is never null. Defaults to an empty string.
        """
        print("Author value before validation:", value)  # 🔥 Debugging line
        return value or ""


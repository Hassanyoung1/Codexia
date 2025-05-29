from rest_framework import generics, permissions
from api.models.bookmark import Bookmark, Highlight
from api.serializers.bookmark_serializer import BookmarkSerializer, HighlightSerializer

class BookmarkListView(generics.ListCreateAPIView):
    """
    API to add & list bookmarks for a user.
    """
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookmarkDeleteView(generics.DestroyAPIView):
    """
    API to delete a bookmark.
    """
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)


class HighlightListView(generics.ListCreateAPIView):
    """
    API to add & list multiple highlights for a user per page.
    """
    serializer_class = HighlightSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns all highlights for a user.
        Supports filtering by book & page.
        """
        queryset = Highlight.objects.filter(user=self.request.user)

        # 🔍 Allow filtering by book & page
        book_id = self.request.query_params.get("book")
        page_number = self.request.query_params.get("page")
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        if page_number:
            queryset = queryset.filter(page_number=page_number)

        return queryset

    def perform_create(self, serializer):
        """
        Saves multiple highlights per page for a user.
        """
        serializer.save(user=self.request.user)


class HighlightDeleteView(generics.DestroyAPIView):
    """
    API to delete a highlight.
    """
    serializer_class = HighlightSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Highlight.objects.filter(user=self.request.user)
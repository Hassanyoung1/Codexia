from rest_framework import generics, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from api.models.book import Book, Category, Tag
from api.serializers.book_serializer import BookSerializer, CategorySerializer, TagSerializer

class UploadBookView(generics.CreateAPIView):
    """
    API to upload a book with categories & tags while preventing duplicate titles.
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        title = self.request.data.get("title")
        existing_book = Book.objects.filter(user=self.request.user, title__iexact=title).first()

        if existing_book:
            return Response({"error": "You have already uploaded a book with this title."}, status=400)
        
        print("Received data:", self.request.data)  # 🔥 Debugging line

        category_name = self.request.data.get("category")  # 🔥 Get category name
        tag_names = self.request.data.getlist("tags")  # 🔥 Get tags as a list

        # 🔥 Find or create category
        category = Category.objects.filter(name__iexact=category_name).first()
        if not category and category_name:
            category = Category.objects.create(name=category_name)

        # 🔥 Find or create tags
        tag_objects = []
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name.lower())  # 🔥 Make tag lowercase
            tag_objects.append(tag)

        # 🔥 Save book with category & tags
        book = serializer.save(user=self.request.user, category=category)
        book.tags.set(tag_objects)


class ListBooksView(generics.ListAPIView):
    """
    API to list all books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    
      # 🔥 Enable search & filtering
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["title", "author"]  # 🔍 Allow searching by title & author
    filterset_fields = ["category", "tags__name"]  # 🔥 Filter by category & tag
    filterset_fields = ["uploaded_at"]  # ⏳ Allow filtering by upload date


class BookDetailView(generics.RetrieveAPIView):
    """
    API to get details of a book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeleteBookView(generics.DestroyAPIView):
    """
    API to delete a book.
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)  # 🔥 Users can only delete their books


class CategoryListView(generics.ListAPIView):
    """
    API to fetch all book categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class TagListView(generics.ListAPIView):
    """
    API to fetch all available book tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
from django.urls import path
from api.views.book_views import UploadBookView, ListBooksView, BookDetailView, DeleteBookView, CategoryListView, TagListView


urlpatterns = [
    path("upload/", UploadBookView.as_view(), name="upload_book"),
    path("", ListBooksView.as_view(), name="list_books"),
    path("<int:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("<int:pk>/delete/", DeleteBookView.as_view(), name="delete_book"),
    path("categories/", CategoryListView.as_view(), name="list_categories"),  
    path("tags/", TagListView.as_view(), name="list_tags"), 
]

from django.urls import path
from api.views.bookmark_views import (
    BookmarkListView,
    BookmarkDeleteView,
    HighlightListView,
    HighlightDeleteView,
)

urlpatterns = [
    # Bookmarks endpoints
    path("bookmarks/", BookmarkListView.as_view(), name="bookmark-list-create"),
    path("bookmarks/<int:pk>/delete/", BookmarkDeleteView.as_view(), name="bookmark-delete"),
    
    # Highlights endpoints
    path("highlights/", HighlightListView.as_view(), name="highlight-list-create"),
    path("highlights/<int:pk>/delete/", HighlightDeleteView.as_view(), name="highlight-delete"),
]
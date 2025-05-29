from django.urls import path, include

urlpatterns = [
    path("auth/", include("api.urls.auth_urls")),  # ✅ Ensure this is included
    path("reading/", include("api.urls.reading_urls")),
    path("badges/", include("api.urls.badge_urls")),
    path("books/", include("api.urls.book_urls")),
    path("highlights/", include("api.urls.bookmark_urls")),
    path("bookmarks/", include("api.urls.bookmark_urls")),
    path("focus/", include("api.urls.focus_urls")), 
]

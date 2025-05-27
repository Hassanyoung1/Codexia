from api.views.auth_views import RegisterView, LoginView, LogoutView, VerifyEmailView
from django.urls import path, include
from api.views.auth_views import welcome_view 
from django.shortcuts import redirect

import sys



def home_redirect(request):
    return redirect("/api/auth/signup/") 

urlpatterns = [   
    path("", welcome_view, name="home"),  # ✅ Now "/" shows a welcome message
    path("auth/", include("api.urls.auth_urls")),
    path("reading/", include("api.urls.reading_urls")),
    path("badges/", include("api.urls.badge_urls")),
    path("books/", include("api.urls.book_urls")),
    path("bookmarks/", include("api.urls.bookmark_urls")),
    path("highlights/", include("api.urls.highlight_urls")),
    path("focus/", include("api.urls.focus_urls")), 

]



# api/urls/__init__.py
from django.urls import path, include
from api.views.user_views import UserProfileView, PasswordChangeView, EmailUpdateView

urlpatterns = [
    # Authentication
    path('auth/', include('api.urls.auth_urls')),
    
  
    
    # User Profile
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/password/', PasswordChangeView.as_view(), name='password-change'),
    path('user/email/', EmailUpdateView.as_view(), name='email-update'),\
    path('accounts/', include('allauth.urls')),

]
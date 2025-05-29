from django.urls import path
from api.views.badge_views import BadgeListView, UserBadgeListView
from api.views.reward_views import UserRewardListView, RedeemRewardView

urlpatterns = [
    path("", BadgeListView.as_view(), name="badge_list"),  # Get all available badges
    path("earned/", UserBadgeListView.as_view(), name="user_badges"),  # Get user's earned badges
    path("rewards/", UserRewardListView.as_view(), name="user_rewards"),
    path("rewards/redeem/<int:pk>/", RedeemRewardView.as_view(), name="redeem_reward"),
]

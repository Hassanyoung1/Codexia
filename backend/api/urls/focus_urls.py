from django.urls import path
from api.views.focus_views import ReadingSessionViewSet, BlockingViewSet

urlpatterns = [
    path("reading/start/", ReadingSessionViewSet.as_view({"post": "start_reading"}), name="start-reading"),
    path("reading/end/", ReadingSessionViewSet.as_view({"post": "end_reading"}), name="end-reading"),
    path("reading/stats/", ReadingSessionViewSet.as_view({"get": "reading_stats"}), name="reading-stats"),
    path("blocking/activate/", BlockingViewSet.as_view({"post": "activate_blocking"}), name="activate-blocking"),
    path("blocking/deactivate/", BlockingViewSet.as_view({"post": "deactivate_blocking"}), name="deactivate-blocking"),
]

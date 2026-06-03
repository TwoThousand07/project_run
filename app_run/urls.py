from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register(r"runs", RunViewSet)
router.register(r"users", UserViewSet, basename="users")
router.register(r"challenges", ChallengeViewSet)
router.register(r"positions", PositionViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "company_details/", CompanyInformationAPIView.as_view(), name="company_details"
    ),
    path("runs/<int:id>/start/", RunStartAPIView.as_view(), name="run_start"),
    path("runs/<int:id>/stop/", RunStopAPIView.as_view(), name="run_stop"),
    path(
        "athlete_info/<int:user_id>/", AthleteInfoAPIView.as_view(), name="athlete_info"
    ),
    path("collectible_item/", CollectibleItemsAPIView.as_view()),
    path("upload_file/", UploadXLSXFilesAPIView.as_view()),
    path("subscribe_to_coach/<int:id>/", SubscripeToCoachAPIView.as_view()),
    path("challenges_summary/", ChallengesSummaryAPIView.as_view()),
    path("rate_coach/<int:coach_id>/", RatingCoachAPIView.as_view()),
    path("analytics_for_coach/<int:coach_id>/", AnalytisForCoachAPIView.as_view()),
]

from django.urls import path, include

from .views import *

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"runs", RunViewSet)
router.register(r"users", UserViewSet, basename="users")
router.register(r"challenges", ChallengeViewSet)
router.register(r"positions", PositionViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("company_details/", CompanyInformationAPIView.as_view(),
         name="company_details"),
    path("runs/<int:id>/start/", RunStartAPIView.as_view(), name="run_start"),
    path("runs/<int:id>/stop/", RunStopAPIView.as_view(), name="run_stop"),

    path("athlete_info/<int:user_id>/",
         AthleteInfoAPIView.as_view(), name="athlete_info"),
    
    path("collectible_item/", CollectibleItemsAPIView.as_view())
]

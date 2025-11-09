from django.urls import path, include

from .views import *

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"runs", RunViewSet)
router.register(r"users", UserViewSet, basename="users")




urlpatterns = [
    path("", include(router.urls)),
    path("company_details/", CompanyInformationAPIView.as_view(), name="company_details"),
    path("runs/<int:id>/start/", RunStartAPIView.as_view(), name="run_start"),
    path("runs/<int:id>/stop/", RunStopAPIView.as_view(), name="run_stop"),
]

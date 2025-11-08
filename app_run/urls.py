from django.urls import path, include

from .views import *

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("runs/", RunViewSet, basename="run")




urlpatterns = [
    path("", include(router.urls)),
    path("company_details/", CompanyInformationAPIView.as_view(), name="company_details")
]

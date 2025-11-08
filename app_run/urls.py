from django.urls import path, include

from .views import *

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"runs", RunViewSet)
router.register(r"users", UserViewSet)




urlpatterns = [
    path("", include(router.urls)),
    path("company_details/", CompanyInformationAPIView.as_view(), name="company_details")
]

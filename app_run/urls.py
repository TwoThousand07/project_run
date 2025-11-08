from django.urls import path

from .views import *

urlpatterns = [
    path("company_details/", CompanyInformationAPIView.as_view(), name="company_details")
]

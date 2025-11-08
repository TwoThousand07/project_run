from django.shortcuts import render
from django.conf import settings


from rest_framework import views
from rest_framework.response import Response



class CompanyInformationAPIView(views.APIView):
    
    def get(self, request):
        return Response({
            "company_name": settings.COMPANY_NAME,
            "slogan": settings.SLOGAN,
            "contacts": settings.CONTACTS
        })

from django.shortcuts import render
from django.conf import settings


from rest_framework import views
from rest_framework import viewsets
from rest_framework.response import Response


from .serializers import RunSerializer
from .models import Run


class CompanyInformationAPIView(views.APIView):
    '''
        Инфорация о странице
    '''
    def get(self, request):
        return Response({
            "company_name": settings.COMPANY_NAME,
            "slogan": settings.SLOGAN,
            "contacts": settings.CONTACTS
        })
        
    
class RunViewSet(viewsets.ModelViewSet):
    '''
        Инфорация о забеге атлета
    '''
    
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    

        



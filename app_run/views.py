from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.models import User


from rest_framework import views
from rest_framework import viewsets
from rest_framework.response import Response


from .serializers import RunSerializer, UserSerializer
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
    
    
class UserViewSet(viewsets.ModelViewSet):
    '''
        Информация о пользователях
    '''
    
    queryset = User.objects.all()
    serializer_class = RunSerializer
    

        



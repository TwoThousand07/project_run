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

    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    '''
        Информация о пользователях
    '''

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = self.queryset.exclude(is_superuser=True)

        type = self.request.query_params.get("type", None)
        if type == "coach":
            qs = qs.filter(is_staff=True)
        elif type == "athlete":
            qs = qs.filter(is_staff=False)
        return qs

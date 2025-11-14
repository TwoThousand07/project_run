from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import RunSerializer, UserSerializer, AthleteInfoSerializer
from .models import Run, AthleteInfo


class CompanyInformationAPIView(APIView):
    '''
        Инфорация о странице
    '''

    def get(self, request):
        return Response({
            "company_name": settings.COMPANY_NAME,
            "slogan": settings.SLOGAN,
            "contacts": settings.CONTACTS
        })


class BasePagination(PageNumberPagination):
    '''
        Пагинация для RUN view
    '''
    page_size_query_param = 'size'


class RunViewSet(viewsets.ModelViewSet):
    '''
        Инфорация о забеге атлета
    '''
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["created_at"]
    filterset_fields = ["status", "athlete"]
    pagination_class = BasePagination
    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer


class RunStartAPIView(APIView):
    '''
        Представление для инициализации старта забега
    '''

    def post(self, request, id):
        try:
            run = Run.objects.get(id=id)
        except Run.DoesNotExist:
            return Response({"error": "Забега с данным айди не существует"}, status=status.HTTP_404_NOT_FOUND)

        if run.status in ("in_progress", "finished"):
            return Response({"error": "Забег уже начат или завершен"}, status=status.HTTP_400_BAD_REQUEST)

        run.status = "in_progress"
        run.save()
        return Response({"message": "Забег успешно начать!"}, status=status.HTTP_200_OK)


class RunStopAPIView(APIView):
    '''
        Представление для инициалзиции завершения забега
    '''

    def post(self, request, id):
        try:
            run = Run.objects.get(id=id)
        except Run.DoesNotExist:
            return Response({"error": "Забега с данным айди не существует"}, status=status.HTTP_404_NOT_FOUND)

        if run.status in ("init", "finished"):
            return Response({"error": "Забег еще не начат или завершен"}, status=status.HTTP_400_BAD_REQUEST)

        run.status = "finished"
        run.save()
        return Response({"message": "Забег успешно завершен!"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    '''
        Информация о пользователях
    '''

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ["date_joined"]
    pagination_class = BasePagination
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        qs = self.queryset.exclude(is_superuser=True)

        type = self.request.query_params.get("type", None)
        if type == "coach":
            qs = qs.filter(is_staff=True)
        elif type == "athlete":
            qs = qs.filter(is_staff=False)
        return qs


class AthleteInfoAPIView(APIView):

    def get(self, request, user_id):

        athlete = get_object_or_404(User, id=user_id)

        athlete_info, created = AthleteInfo.objects.prefetch_related(
            "athlete").get_or_create(athlete=athlete)

        return Response({
                "user_id": user_id,
                "goals": athlete_info.goals,
                "weight": athlete_info.weight}, status=status.HTTP_200_OK)

    def put(self, request, user_id):

        data = request.data
        athlete_serializer = AthleteInfoSerializer(data=data)
        if athlete_serializer.is_valid():
            if athlete_serializer.data.weight > 0 and athlete_serializer.data.weight < 900:
                
                athlete = get_object_or_404(User, id=user_id)
                
                athlete_info, created = AthleteInfo.objects.prefetch_related("athlete").update_or_create(athlete=athlete, defaults={
                    "goals": data.get("goals"),
                    "weight": int(data.get("weight"))
                })

                return Response(
                athlete_serializer.data, 
                status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Вес должен быть больше 0 и меньше 900!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Валидация сериализатора не прошла!"}, status=status.HTTP_400_BAD_REQUEST)
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Max, Min, Count, Q, Avg

from rest_framework.pagination import PageNumberPagination

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (RunSerializer,
                          UserSerializer,
                          UserDetailSerializer,
                          AthleteInfoSerializer,
                          ChallengeSerializer,
                          PositionSerializer,
                          CollectibleItemSerializer)
from .models import (Run,
                     AthleteInfo,
                     Challenge,
                     Position,
                     CollectibleItem)

from .services import calculate_total_run_distance, creating_challenges_for_finished_runs
from .utils import import_xlsx_from_file


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

        '''
            После окончания забега, добавляем расстояние между двумя точками в общую Distance поле модели Run, чтобы получить дистанцию за весь забег
        '''

        run.status = "finished"
        run.distance = calculate_total_run_distance(run)

        # Вычисляем общее количество времени потраченное на забег и среднюю скорость
        aggregated_fields = run.position_set.aggregate(
            max_date=Max("date_time"),
            min_date=Min("date_time"),

            # avg_speed
            avg_speed=Avg("speed"),
        )

        if aggregated_fields["min_date"] and aggregated_fields["max_date"]:
            run.run_time_seconds = (
                aggregated_fields["max_date"] - aggregated_fields["min_date"]).total_seconds()
        else:
            run.run_time_seconds = 0

        # В поле speed добавляем среднюю скорость от всех позиции run
        avg_speed = aggregated_fields["avg_speed"]

        run.save()

        creating_challenges_for_finished_runs(run)

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
        qs = self.queryset.annotate(
            runs_finished=Count("run", filter=Q(run__status="finished"))
        ).exclude(is_superuser=True)

        type = self.request.query_params.get("type", None)
        if type == "coach":
            qs = qs.filter(is_staff=True)
        elif type == "athlete":
            qs = qs.filter(is_staff=False)

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return UserSerializer
        if self.action == "retrieve":
            return UserDetailSerializer

        return super().get_serializer_class()


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

        athlete_serializer = AthleteInfoSerializer(data=request.data)
        if athlete_serializer.is_valid(raise_exception=True):
            athlete = get_object_or_404(User, id=user_id)

            athlete_info, created = AthleteInfo.objects.prefetch_related("athlete").update_or_create(athlete=athlete, defaults={
                "goals": athlete_serializer.validated_data.get("goals", None),
                "weight": athlete_serializer.validated_data.get("weight", None)
            })

            return Response(
                athlete_serializer.data,
                status=status.HTTP_201_CREATED)


class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.select_related("athlete").all()
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        athlete = self.request.query_params.get("athlete")

        if athlete:
            return self.queryset.filter(athlete=athlete)

        return self.queryset


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.select_related("run").all()
    serializer_class = PositionSerializer

    def get_queryset(self):
        run = self.request.query_params.get("run")

        if run:
            return self.queryset.filter(run=run)

        return self.queryset


class CollectibleItemsAPIView(APIView):
    def get(self, request):
        queryset = CollectibleItem.objects.all()
        serializer_class = CollectibleItemSerializer(queryset, many=True)

        return Response(serializer_class.data)


class UploadXLSXFilesAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES['file']

        result = import_xlsx_from_file(uploaded_file)

        return Response(result, status=status.HTTP_200_OK)

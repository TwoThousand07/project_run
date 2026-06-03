from posix import stat

from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    AthleteInfo,
    Challenge,
    CollectibleItem,
    Position,
    Rating,
    Run,
    Subscripe,
)
from .serializers import (
    AthleteInfoSerializer,
    ChallengeSerializer,
    CollectibleItemSerializer,
    PositionSerializer,
    RunSerializer,
    UserAthleteDetailSerializer,
    UserCoachDetailSerializer,
    UserSerializer,
)
from .services import (
    calculate_total_run_distance,
    creating_challenges_for_finished_runs,
)
from .utils import calculate_distance_between_two_positions, import_xlsx_from_file


class CompanyInformationAPIView(APIView):
    """
    Инфорация о странице
    """

    def get(self, request):
        return Response(
            {
                "company_name": settings.COMPANY_NAME,
                "slogan": settings.SLOGAN,
                "contacts": settings.CONTACTS,
            }
        )


class BasePagination(PageNumberPagination):
    """
    Пагинация для RUN view
    """

    page_size_query_param = "size"


class RunViewSet(viewsets.ModelViewSet):
    """
    Инфорация о забеге атлета
    """

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["created_at"]
    filterset_fields = ["status", "athlete"]
    pagination_class = BasePagination
    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer


class RunStartAPIView(APIView):
    """
    Представление для инициализации старта забега
    """

    def post(self, request, id):
        try:
            run = Run.objects.get(id=id)
        except Run.DoesNotExist:
            return Response(
                {"error": "Забега с данным айди не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if run.status in ("in_progress", "finished"):
            return Response(
                {"error": "Забег уже начат или завершен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        run.status = "in_progress"
        run.save()
        return Response({"message": "Забег успешно начать!"}, status=status.HTTP_200_OK)


class RunStopAPIView(APIView):
    """
    Представление для инициалзиции завершения забега
    """

    def post(self, request, id):
        try:
            run = Run.objects.get(id=id)
        except Run.DoesNotExist:
            return Response(
                {"error": "Забега с данным айди не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if run.status in ("init", "finished"):
            return Response(
                {"error": "Забег еще не начат или завершен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        """
            После окончания забега, добавляем расстояние между двумя точками в общую Distance поле модели Run, чтобы получить дистанцию за весь забег
        """

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
                aggregated_fields["max_date"] - aggregated_fields["min_date"]
            ).total_seconds()
        else:
            run.run_time_seconds = 0

        # В поле speed добавляем среднюю скорость от всех позиции run
        avg_speed = aggregated_fields["avg_speed"]

        run.speed = avg_speed

        run.save()

        creating_challenges_for_finished_runs(run)

        return Response(
            {"message": "Забег успешно завершен!"}, status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Информация о пользователях
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ["date_joined"]
    pagination_class = BasePagination
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        qs = self.queryset.annotate(
            runs_finished=Count("run", filter=Q(run__status="finished")),
            rating=Avg("ratings__rating"),
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
            user_id = self.kwargs.get("pk")
            if self.get_queryset().filter(is_staff=True, id=user_id).exists():
                return UserCoachDetailSerializer
            return UserAthleteDetailSerializer

        return super().get_serializer_class()


class AthleteInfoAPIView(APIView):
    def get(self, request, user_id):

        athlete = get_object_or_404(User, id=user_id)

        athlete_info, created = AthleteInfo.objects.prefetch_related(
            "athlete"
        ).get_or_create(athlete=athlete)

        return Response(
            {
                "user_id": user_id,
                "goals": athlete_info.goals,
                "weight": athlete_info.weight,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, user_id):

        athlete_serializer = AthleteInfoSerializer(data=request.data)
        if athlete_serializer.is_valid(raise_exception=True):
            athlete = get_object_or_404(User, id=user_id)

            athlete_info, created = AthleteInfo.objects.prefetch_related(
                "athlete"
            ).update_or_create(
                athlete=athlete,
                defaults={
                    "goals": athlete_serializer.validated_data.get("goals", None),
                    "weight": athlete_serializer.validated_data.get("weight", None),
                },
            )

            return Response(athlete_serializer.data, status=status.HTTP_201_CREATED)


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

    def perform_create(self, serializer):
        instance = serializer.save()  # runner2 - latitude:12.0000, longitude:35.0000
        try:
            position_before = Position.objects.filter(run=instance.run).order_by(
                "-date_time"
            )[1]

            distance_between_before_and_now = calculate_distance_between_two_positions(
                (position_before.latitude, position_before.longitude),
                (instance.latitude, instance.longitude),
                measurement="m",
            )
            timedelta_between = instance.date_time - position_before.date_time

            instance.speed = round(
                distance_between_before_and_now / timedelta_between.total_seconds(), 2
            )
            instance.distance = round(
                (distance_between_before_and_now * 0.001) + position_before.distance, 2
            )

            instance.save()
        except IndexError:
            instance.save()


class CollectibleItemsAPIView(APIView):
    def get(self, request):
        queryset = CollectibleItem.objects.all()
        serializer_class = CollectibleItemSerializer(queryset, many=True)

        return Response(serializer_class.data)


class UploadXLSXFilesAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES["file"]

        result = import_xlsx_from_file(uploaded_file)

        return Response(result, status=status.HTTP_200_OK)


class SubscripeToCoachAPIView(APIView):
    def post(self, request, id):
        coach_id = id
        athlete_id = request.data.get("athlete")

        try:
            coach = User.objects.get(id=coach_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Тренера с данным айди не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            athlete = User.objects.get(id=athlete_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Атлета с данным айди не существует"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (not coach.is_staff) or (athlete.is_staff):
            return Response(
                {
                    "error": "Подписываться могут только athlete, и можно подписываться только к coach"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            Subscripe.objects.create(coach=coach, athlete=athlete)
        except IntegrityError:
            return Response(
                {"error": "Подписаться можно лишь один раз"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": f"Атлет {athlete_id} успешно подписался на тренера {coach_id}"},
            status=status.HTTP_200_OK,
        )


class ChallengesSummaryAPIView(APIView):
    def get(self, request):
        response = []

        for ch in set(
            Challenge.objects.all()
            .select_related("athlete")
            .values_list("full_name", flat=True)
        ):
            res = {}
            res["name_to_display"] = ch

            athlethes = []
            for usr in User.objects.filter(challenges__full_name=ch):
                athlete = {}
                athlete["id"] = usr.id
                athlete["full_name"] = f"{usr.first_name} {usr.last_name}"
                athlete["username"] = usr.username

                athlethes.append(athlete)

            res["athletes"] = athlethes

            response.append(res)

        return Response(response)


class RatingCoachAPIView(APIView):
    def post(self, request, coach_id):
        athlete_id = request.data.get("athlete")
        rating = request.data.get("rating")

        try:
            athlete = User.objects.get(id=athlete_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Атлета с данным айди не существует"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            coach = User.objects.get(id=coach_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Тренера с данным айди не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            Subscripe.objects.get(coach=coach, athlete=athlete)
        except Subscripe.DoesNotExist:
            return Response(
                {
                    "error": "Атлет должен быть подписан на тренера, чтобы поставить ему рейтинг"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if rating:
            try:
                rating = int(rating)

                if not (1 <= rating <= 5):
                    return Response(
                        {"error": "Рейтинг должен быть в диапазоне с 1 до 5"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except ValueError:
                return Response(
                    {"error": "Рейтинг должен быть числом"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "Передайте рейтинг"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            Rating.objects.update_or_create(
                athlete=athlete, coach=coach, defaults={"rating": rating}
            )
        except IntegrityError:
            return Response(
                {"error": "Атлет может лишь один раз поставить рейтинг этому тренеру"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": f"Атлет {athlete.username} поставил тренеру {coach.username} рейтинг {rating}"
            }
        )


class AnalytisForCoachAPIView(APIView):
    def get(self, request, coach_id):

        try:
            coach = User.objects.get(id=coach_id)
        except User.DoesNotExist:
            return Response({"error": "Тренера с данным айди не существует"},
                status=status.HTTP_404_NOT_FOUND)

        

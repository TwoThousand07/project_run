from django.db.models import F, Window, Sum
from django.db.models.functions import Lag

from .models import Position, Run, Challenge
from .utils import calculate_distance_between_two_positions


def calculate_total_run_distance(run_instance: Run) -> float:
    '''
        Вычисляем общую дистанцию забега
    '''

    positions = Position.objects.filter(run=run_instance).annotate(
        prev_lat=Window(
            expression=Lag("latitude"),
            order_by=F("id").asc()
        ),
        prev_lon=Window(
            expression=Lag("longitude"),
            order_by=F("id").asc()
        )
    )

    total_distance = 0.0

    for pos in positions:
        if pos.prev_lat is None and pos.prev_lon is None:
            continue

        total_distance += calculate_distance_between_two_positions(
            (pos.prev_lat, pos.prev_lon),
            (pos.latitude, pos.longitude)
        )

    return total_distance


def creating_challenges_for_finished_runs(run_instance: Run) -> None:
    '''
        Создаем челленджи для завершеных забегов
    '''

    '''
        Если пользователь завершает 10 забегов, мы даем ему достижение "Сделай 10 Забегов!"
    '''
    if Run.objects.filter(athlete=run_instance.athlete, status="finished").count() == 10:
        Challenge.objects.create(
            athlete=run_instance.athlete, full_name="Сделай 10 Забегов!")

    '''
        Если пользователь пробежал 50 км или больше, мы даем ему достижение "Пробеги 50 километров"!
    '''
    total_distance_of_all_runs_user = Run.objects.filter(athlete=run_instance.athlete, status="finished").aggregate(
        result=Sum("distance")
    )

    if total_distance_of_all_runs_user["result"] != None:
        if total_distance_of_all_runs_user["result"] >= 50:
            Challenge.objects.create(
                athlete=run_instance.athlete, full_name="Пробеги 50 километров!"
            )

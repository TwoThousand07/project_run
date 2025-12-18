from geopy.distance import geodesic

from .models import Position, Run, Challenge

from django.contrib.auth.models import User


def calculate_distance_between_two_positions(start_pos: Position, end_pos: Position) -> float:
    '''
    Docstring для calculate_distance_between_two_positions
    
    :param start_pos: Начальная точка
    :type start_pos: Position
    :param end_pos: Конец точки
    :type end_pos: Position
    :return: Возвращаем дистанцию между двумя точками
    :rtype: float
    '''
    start = (start_pos.latitude, start_pos.longitude)
    end = (end_pos.latitude, end_pos.longitude)

    return geodesic(start, end).km


def create_challenge_for_run(athlete: User, full_name: str, value, *args) -> Challenge:
    pass


# '''
#     Если пользователь завершает 10 забегов, мы даем ему достижение "Сделай 10 Забегов!"
# '''
# if Run.objects.filter(athlete=run.athlete, status="finished").count() == 10:
#     Challenge.objects.create(
#         athlete=run.athlete, full_name="Сделай 10 Забегов!")
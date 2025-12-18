from geopy.distance import geodesic

from .models import Position


def calculate_distance_between_two_positions(start: tuple, end: tuple) -> float:
    '''
    Docstring для calculate_distance_between_two_positions

    :param start_pos: Начальная точка
    :type start_pos: Position
    :param end_pos: Конец точки
    :type end_pos: Position
    :return: Возвращаем дистанцию между двумя точками
    :rtype: float
    '''

    return geodesic(start, end).km

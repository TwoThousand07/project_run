from geopy.distance import geodesic

from .models import Position


def calculate_distance_between_two_positions(start_pos: Position, end_pos: Position) -> float:
    start = (start_pos.latitude, start_pos.longitude)
    end = (end_pos.latitude, end_pos.longitude)

    return geodesic(start, end).meters

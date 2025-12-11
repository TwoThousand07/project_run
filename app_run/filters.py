import django_filters

from .models import Position, Challenge


class PositionFilter(django_filters.FilterSet):

    run = django_filters.CharFilter(
        field_name="run__id",
        lookup_expr="exact"
    )

    class Meta:
        model = Position
        fields = ["run", "longitude", "latitude"]


class ChallengeFilter(django_filters.FilterSet):
    
    athlete = django_filters.CharFilter(
        field_name="athlete__id",
        lookup_expr="exact"
    )
    
    class Meta:
        model = Challenge
        fields = "__all__"
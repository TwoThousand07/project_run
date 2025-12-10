import django_filters

from .models import Position


class PositionFilter(django_filters.FilterSet):

    run = django_filters.CharFilter(
        field_name="run__id",
        lookup_expr="exact"
    )

    class Meta:
        model = Position
        fields = ["run", "longitude", "latitude"]

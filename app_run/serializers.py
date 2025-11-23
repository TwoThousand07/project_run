from rest_framework import serializers

from .models import Run, AthleteInfo, Challenge

from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "date_joined", "username",
                  "last_name", "first_name", "type", "runs_finished"]

    def get_type(self, obj):
        if obj.is_staff:
            return "coach"
        return "athlete"

    def get_runs_finished(self, obj):
        return Run.objects.filter(athlete=obj, status="finished").count()


class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "last_name", "first_name"]


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(read_only=True, source="athlete")

    class Meta:
        model = Run
        fields = "__all__"


class AthleteInfoSerializer(serializers.Serializer):
    athlete = UserSerializer(read_only=True)
    weight = serializers.IntegerField(required=False)
    goals = serializers.CharField(required=False)
    
    def validate_weight(self, value):
        if not(value > 0 and value < 900):
            raise serializers.ValidationError("Вес должен быть больше 0 и меньше 900!")
        return value
    

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = "__all__"
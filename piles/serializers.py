from rest_framework import serializers
from .models import Pile

class PileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pile
        fields = "__all__"
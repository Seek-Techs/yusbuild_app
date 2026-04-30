from rest_framework.viewsets import ModelViewSet
from .models import Pile
from .serializers import PileSerializer
from .services.calculations import calculate_pile


class PileViewSet(ModelViewSet):
    queryset = Pile.objects.all()
    serializer_class = PileSerializer

    def perform_create(self, serializer):
        pile = serializer.save()

        result = calculate_pile(pile)

        pile.total_length = result["total_length"]
        pile.total_weight = result["total_weight"]
        pile.save()
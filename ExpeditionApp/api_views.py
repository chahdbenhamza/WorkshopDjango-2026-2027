from rest_framework import viewsets
from .models import Expedition
from .serializers import ExpeditionSerializer

class ExpeditionViewSet(viewsets.ModelViewSet):
    queryset=Expedition.objects.all()
    serializer_class=ExpeditionSerializer
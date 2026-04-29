from django.shortcuts import render
from .models import Genre
from .serializers import GenreSerializer
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

# ==================== Genre ViewSet ====================
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    http_method_names = ['get', 'post', 'put', 'patch']

    
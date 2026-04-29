from .models import Genre,Music
from .serializers import GenreSerializer,MusicSerializer
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .paginations import MusicPagination
from rest_framework.permissions import  IsAuthenticatedOrReadOnly
from django.db.models import F,Case,When,IntegerField
# Create your views here.

# ==================== Genre ViewSet ====================
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    http_method_names = ['get', 'post', 'put', 'patch']

# ==================== Music ViewSet ====================
class MusicModelViewSet(viewsets.ModelViewSet):
  serializer_class =MusicSerializer
  queryset=Music.objects.all().order_by('uploaded_at')
  permission_classes = [IsAuthenticatedOrReadOnly]
  pagination_class = MusicPagination

  def get_queryset(self):
        qs = Music.objects.all().order_by('uploaded_at')
        if self.request.query_params.get('order_in_genre') == '2':
            qs = qs.annotate(
                is_negative=Case(
                    When(like__lt=F('dislike'), then=1),default=0,output_field=IntegerField(),)
            ).order_by('is_negative', 'uploaded_at')
        return qs
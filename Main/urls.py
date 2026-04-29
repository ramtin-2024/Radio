# Global_music/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, MusicViewSet


router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'musics', MusicViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
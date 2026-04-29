# Global_music/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GenreViewSet, MusicViewSet, LikeDislikeViewSet,
    CurrentStatusAPIView, test_queue   # اضافه کردن CurrentStatusAPIView
)

router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'musics', MusicViewSet)
router.register(r'votes', LikeDislikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
from rest_framework import serializers
from .models import Music, LikeDislike, Genre
from django.utils import timezone
import zoneinfo

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'created_at', 'start_time']

class MusicSerializer(serializers.ModelSerializer):
    audio_file_url = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    genre_name = serializers.ReadOnlyField(source='genre.name')
    estimated_start = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    net_vote = serializers.ReadOnlyField()

    class Meta:
        model = Music
        fields = [
            'id', 'estimated_start', 'order_in_genre', 'title', 'artist', 'duration', 'uploaded_at',
            'audio_file', 'audio_file_url', 'cover_image', 'cover_image_url',
            'genre', 'genre_name', 'likes_count', 'dislikes_count', 'net_vote',
            'retry_count', 'is_active',
        ]
        read_only_fields = ['title', 'artist', 'duration', 'uploaded_at', 'retry_count', 'is_active']

    def get_audio_file_url(self, obj):
        request = self.context.get('request')
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_file.url)
        return None

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    def get_estimated_start(self, obj):
        estimated_starts = self.context.get('estimated_starts')
        if estimated_starts and obj.id in estimated_starts:
            return estimated_starts[obj.id].isoformat()
        return None

    def get_likes_count(self, obj):
        return obj.likes.filter(vote=LikeDislike.LIKE).count()

    def get_dislikes_count(self, obj):
        return obj.likes.filter(vote=LikeDislike.DISLIKE).count()

class LikeDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeDislike
        fields = ['id', 'music', 'vote', 'created_date']
        read_only_fields = ['created_date']
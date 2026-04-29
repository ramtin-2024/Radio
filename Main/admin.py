from django.contrib import admin
from .models import Music, Genre

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist','like', 'dislike', 'duration', 'is_active', 'retry_count', 'order_in_genre')
    list_filter = ('is_active', 'genre')
    search_fields = ('title', 'artist')
    readonly_fields = ('title', 'artist', 'duration', 'uploaded_at', 'order_in_genre')
    fieldsets = (
        (None, {'fields': ('audio_file', 'cover_image', 'genre')}),
        ('اطلاعات خودکار', {'fields': ('title', 'artist', 'duration', 'uploaded_at', 'order_in_genre','like', 'dislike')}),
        ('مدیریت', {'fields': ('is_active', 'retry_count')}),
    )

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'created_at')
    search_fields = ('name',)
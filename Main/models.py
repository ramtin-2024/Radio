import os
import io
from django.db import models
from django.core.files import File
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from django.conf import settings
from rest_framework.exceptions import ValidationError

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام ژانر")
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="زمان شروع ژانر")

    class Meta:
        verbose_name = "ژانر"
        verbose_name_plural = "ژانرها"
        ordering = ['name']

    def __str__(self):
        return self.name

class Music(models.Model):
    audio_file = models.FileField(upload_to='music_uploads/', verbose_name="فایل موزیک")
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True, verbose_name="کاور")

    title = models.CharField(max_length=200, blank=True, verbose_name="عنوان ترانه")
    artist = models.CharField(max_length=200, blank=True, verbose_name="نام خواننده")
    duration = models.CharField(max_length=10, blank=True, verbose_name="مدت زمان")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان آپلود")
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, verbose_name="ژانر")
    order_in_genre = models.PositiveIntegerField(default=0, editable=False, verbose_name="شماره در ژانر")
    retry_count = models.PositiveIntegerField(default=0, verbose_name="تعداد دفعات عقب‌افتادگی")
    is_active = models.BooleanField(default=True, verbose_name="فعال برای پخش")

    @property
    def net_vote(self):
        likes = self.likes.filter(vote=LikeDislike.LIKE).count()
        dislikes = self.likes.filter(vote=LikeDislike.DISLIKE).count()
        return likes - dislikes

    class Meta:
        verbose_name = "موزیک"
        verbose_name_plural = "موزیک‌ها"

    def __str__(self):
        return self.title if self.title else os.path.basename(self.audio_file.name)

    def save(self, *args, **kwargs):
        if getattr(self, '_metadata_extracted', False):
            super().save(*args, **kwargs)
            return

        is_new = self.pk is None
        if is_new and self.genre_id:
            max_order = Music.objects.filter(genre=self.genre).aggregate(models.Max('order_in_genre'))['order_in_genre__max']
            self.order_in_genre = (max_order or 0) + 1

        super().save(*args, **kwargs)

        try:
            file_path = self.audio_file.path
            audio = MutagenFile(file_path)

            if audio and hasattr(audio.info, 'length'):
                total_seconds = int(audio.info.length)
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                self.duration = f"{minutes}:{seconds:02d}"
            else:
                raise ValidationError({"audio_file": "مدت زمان فایل قابل استخراج نیست."})

            try:
                tags = EasyID3(file_path)
                if 'title' in tags:
                    self.title = tags['title'][0]
                else:
                    raise ValidationError({"audio_file": "فایل MP3 دارای تگ title نیست."})
                if 'artist' in tags:
                    self.artist = tags['artist'][0]
                else:
                    raise ValidationError({"audio_file": "فایل MP3 دارای تگ artist نیست."})
            except Exception:
                raise ValidationError({"audio_file": "متادیتای فایل قابل خواندن نیست. لطفاً یک فایل MP3 معتبر با تگ‌های title و artist آپلود کنید."})

            if self.audio_file.name.lower().endswith('.mp3') and not self.cover_image:
                try:
                    tags_id3 = ID3(file_path)
                    for tag in tags_id3.getall('APIC'):
                        if isinstance(tag, APIC):
                            image_io = io.BytesIO(tag.data)
                            ext = 'jpg'
                            if tag.mime == 'image/png':
                                ext = 'png'
                            elif tag.mime == 'image/jpeg':
                                ext = 'jpg'
                            file_name = f"cover_{self.pk}.{ext}"
                            self.cover_image.save(file_name, File(image_io), save=False)
                            break
                except Exception:
                    pass

            self._metadata_extracted = True
            self.save(update_fields=['title', 'artist', 'duration', 'cover_image'])

        except ValidationError:
            self.audio_file.delete(save=False)
            raise
        except Exception as e:
            self.audio_file.delete(save=False)
            raise ValidationError({"audio_file": f"خطا در پردازش فایل: {str(e)}"})



import os,io
from django.db import models
from django.core.files import File
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from datetime import timedelta
from django.core.exceptions import ValidationError   
from django.core.validators import FileExtensionValidator


class Genre(models.Model):

    name = models.CharField(max_length=100, unique=True, verbose_name="نام ژانر")
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="زمان شروع ژانر")

    class Meta:
        verbose_name = "ژانر"
        verbose_name_plural = "ژانرها"
        ordering = ['name']

    def __str__(self):return self.name

class Music(models.Model):

    audio_file = models.FileField(upload_to='music_uploads/', verbose_name="فایل موزیک",validators=[FileExtensionValidator(allowed_extensions=['mp3'])])
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True, verbose_name="کاور",validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    title = models.CharField(max_length=200, blank=True, verbose_name="عنوان ترانه")
    artist = models.CharField(max_length=200, blank=True, verbose_name="نام خواننده")
    duration = models.DurationField(blank=True, null=True, verbose_name="مدت زمان")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان آپلود")
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, verbose_name="ژانر")
    order_in_genre = models.PositiveIntegerField(default=0, editable=False, verbose_name="شماره در ژانر")
    retry_count = models.PositiveIntegerField(default=0, verbose_name="تعداد دفعات عقب‌افتادگی")
    is_active = models.BooleanField(default=True, verbose_name="فعال برای پخش")
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
    

    class Meta:
        ordering = ['genre', 'uploaded_at']

    def __str__(self):return self.title if self.title else os.path.basename(self.audio_file.name)
    
    @property
    def popularity(self):return self.like - self.dislike

    def extract_metadata(self):
        path = self.audio_file.path
        audio = MutagenFile(path)
        if not audio or not hasattr(audio.info, 'length'):
            raise ValidationError("مدت زمان قابل استخراج نیست")

        self.duration = timedelta(seconds=int(audio.info.length))

        try:
            tags = EasyID3(path)
            self.title = tags.get('title', [None])[0] or self.title
            self.artist = tags.get('artist', [None])[0] or self.artist
        except Exception:
            raise ValidationError("متادیتا خوانده نشد (نیاز به تگ title و artist)")

        if not self.title or not self.artist:
            raise ValidationError("فایل فاقد تگ title یا artist است")

        # استخراج کاور فقط برای MP3
        if path.lower().endswith('.mp3') and not self.cover_image:
            try:
                for tag in ID3(path).getall('APIC'):
                    ext = 'jpg' if tag.mime == 'image/jpeg' else 'png' if tag.mime == 'image/png' else 'jpg'
                    self.cover_image.save(f"cover_{self.pk}.{ext}", File(io.BytesIO(tag.data)), save=False)
                    break
            except Exception:
                pass

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and self.genre_id:
            max_order = Music.objects.filter(genre=self.genre).aggregate(models.Max('order_in_genre'))['order_in_genre__max']
            self.order_in_genre = (max_order or 0) + 1

        super().save(*args, **kwargs)

        if is_new:
            try:
                self.extract_metadata()
                super().save(update_fields=['title', 'artist', 'duration', 'cover_image'])
            except ValidationError:
                self.audio_file.delete(save=False)
                raise
from django.contrib import admin

from .models import Image, ImageData


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("image_id", "filename", "uploader", "status", "created_at")
    list_filter = ("status", "mime_type")
    search_fields = ("filename", "checksum", "image_id")


@admin.register(ImageData)
class ImageDataAdmin(admin.ModelAdmin):
    list_display = ("image", "created_at")

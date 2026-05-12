from django.contrib import admin
from .models import Artwork
from django.utils.html import format_html


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'price', 'is_visible', 'created_at')
    list_filter = ('is_visible',)
    search_fields = ('title',)

    fields = ('title', 'description', 'image', 'price', 'is_visible')
    readonly_fields = ('created_at',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" />', obj.image.url)
        return ""

    image_preview.short_description = 'Preview'
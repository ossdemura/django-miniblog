from __future__ import unicode_literals

from django.contrib import admin
from .models import Post  # from post.models import Post

# Register your models here.

class PostModelAdmin(admin.ModelAdmin):
    list_display = ["titulo", "actualizado", "timestamp"]
    list_display_links = ["actualizado"]
    list_filter = ["timestamp"]
    list_editable = ["titulo"]
    search_fields = ["titulo", "contenido"]

    class Meta:
        model = Post

# Registrar el model en el admin

admin.site.register(Post, PostModelAdmin)
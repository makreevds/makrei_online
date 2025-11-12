from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at", "user")
    search_fields = ("title", "content", "user__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

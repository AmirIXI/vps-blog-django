from django.contrib import admin
from .models import Post, Comment, Vote

class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'created', 'updated']
    search_fields = ['body', 'title']
    list_filter = ['user', 'created', 'updated']
    raw_id_fields = ['user']
    prepopulated_fields = {
        'slug': ['body']
    }


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'is_reply']
    raw_id_fields = ['user', 'post', 'reply']
    search_fields = ['body']


admin.site.register(Comment, CommentAdmin)


admin.site.register(Vote)
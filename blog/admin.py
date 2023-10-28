from django.contrib import admin
from blog.models import Post, Tag, Comment


admin.site.register(Tag)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ('author', 'post')
    list_display = ('author', 'post', 'text', 'published_at')
    search_fields = ('author', 'post', 'text')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ('author', 'likes', 'tags')
    list_display = ('title', 'author', 'slug', 'image', 'published_at')
    search_fields = ('title', 'author', 'slug', 'text')
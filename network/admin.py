from django.contrib import admin
from .models import *

class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "body", "date_created")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "body", "date_created")

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(User)
admin.site.register(Comment, CommentAdmin)
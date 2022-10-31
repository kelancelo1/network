
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("post/<int:post_id>", views.post, name="post"),
    path("user/<int:user_id>", views.user, name="user"),
    path("following", views.following, name="following"),
    path("comments/<int:post_id>", views.comments, name="comments")
]

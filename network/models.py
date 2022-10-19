from tokenize import blank_re
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", blank=True, related_name="followers", symmetrical=False)
    liked_posts = models.ManyToManyField("Post", blank=True, related_name="likers")

    def __str__(self):
        return self.username

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "following": list(self.following.values_list("id", flat=True)),
            "followers": list(self.followers.values_list("id", flat=True))
        }
    
    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author}, {self.post}: {self.body}"
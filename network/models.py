from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", blank=True, related_name="followers", symmetrical=False)
    liked_posts = models.ManyToManyField("Post", blank=True, related_name="likers")

    def __str__(self):
        return f"{self.id}: {self.username}"
    
    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author}: {self.body}, {self.date_created}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} -> {self.post}: {self.body}"

    def serialize(self):
        return {
            "author": self.author.username,
            "body": self.body,
            "date_created": self.date_created.strftime("%b. %#d, %Y, %#I:%M %p")
        }
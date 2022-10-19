from django.test import TestCase, Client
from .models import *
from django.db.models import Max

# Create your tests here.

class AllTestCase(TestCase):

    def setUp(self):
        # Create users.
        u1 = User.objects.create_user("username1", "email1", "password1")
        u2 = User.objects.create_user("username2", "email2", "password2")
        u3 = User.objects.create_user("username3", "email3", "password3")
        u1.save()
        u2.save()
        u3.save()

        # Create posts.
        p1 = Post.objects.create(author=u1, body="post1")
        p2 = Post.objects.create(author=u1, body="post2")
        p3 = Post.objects.create(author=u1, body="post3")
        p4 = Post.objects.create(author=u2, body="post4")
        p5 = Post.objects.create(author=u2, body="post5")
        p6 = Post.objects.create(author=u3, body="post6")
        p7 = Post.objects.create(author=u3, body="post7")

        # Create comments.
        c1 = Comment.objects.create(author=u1, post=p4, body="comment1")
        c2 = Comment.objects.create(author=u1, post=p4, body="comment2")
        c3 = Comment.objects.create(author=u2, post=p4, body="comment3")
        c4 = Comment.objects.create(author=u2, post=p4, body="comment4")
        
        # Add user's followers.
        u2.followers.add(u1)
        u2.followers.add(u3)

        # Add users' liked posts.
        u2.liked_posts.add(p4)
        u2.liked_posts.add(p5)
        u2.liked_posts.add(p6)
        u1.liked_posts.add(p4)
        u3.liked_posts.add(p4)

    def test_user_count(self):
        users = User.objects.all()
        self.assertEqual(users.count(), 3)

    def test_post_count(self):
        posts = Post.objects.all()
        self.assertEqual(posts.count(), 7)

    def test_comment_count(self):
        comments = Comment.objects.all()
        self.assertEqual(comments.count(), 4)

    def test_user_posts_count(self):
        u1 = User.objects.get(pk=1)
        self.assertEqual(u1.posts.count(), 3)

    def test_user_comments_count(self):
        u1 = User.objects.get(pk=1)
        self.assertEqual(u1.comments.count(), 2)

    def test_user_followers_count(self):
        u2 = User.objects.get(pk=2)
        self.assertEqual(u2.followers.count(), 2)

    def test_user_following_count(self):
        u1 = User.objects.get(pk=1)
        self.assertEqual(u1.following.count(), 1)

    def test_user_liked_posts_count(self):
        u2 = User.objects.get(pk=2)
        self.assertEqual(u2.liked_posts.count(), 3)

    def test_post_comments_count(self):
        p4 = Post.objects.get(pk=4)
        self.assertEqual(p4.comments.count(), 4)

    def test_post_likers_count(self):
        p4 = Post.objects.get(pk=4)
        self.assertEqual(p4.likers.count(), 3)

    def test_index(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"].paginator.count, 7)

    def test_valid_profile_page(self):
        max_id = User.objects.all().aggregate(Max("id"))["id__max"]
        c = Client()
        response = c.get(f"/user/{max_id}")
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_profile_page(self):
        max_id = User.objects.all().aggregate(Max("id"))["id__max"]
        c = Client()
        response = c.get(f"/user/{max_id + 1}")
        self.assertEqual(response.status_code, 404)

    def test_comments_json_1(self):
        c = Client()
        response = c.get(f"/comments/4")
        self.assertEqual(response.json()["comment_count"], 4)
    
    def test_comments_json_2(self):
        c = Client()
        response = c.get(f"/comments/1")
        self.assertEqual(response.json()["comment_count"], 0)
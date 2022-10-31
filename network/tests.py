from django.test import TestCase, Client
from .models import *
from django.urls import reverse


def create_test_data(cls):
    # Create users.
    cls.u1 = User.objects.create_user("username1", "email1", "password1")
    cls.u2 = User.objects.create_user("username2", "email2", "password2")
    cls.u1.save()
    cls.u2.save()
    # Create posts.
    cls.p1 = Post.objects.create(author=cls.u1, body="post1")
    cls.p2 = Post.objects.create(author=cls.u2, body="post2")
    # Create comment.
    cls.c1 = Comment.objects.create(author=cls.u1, post=cls.p2, body="test comment")
    # Add follower.
    cls.u1.followers.add(cls.u2)
    # Create authenticated client.
    cls.c = Client()
    cls.c.login(username="username1", password="password1")

    
class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    @classmethod
    def check_rendered_templates(cls, response):
        return (
            sorted({
                "network/layout.html", 
                "network/index.html", 
                "network/posts_template.html", 
                "network/user_list_template.html"
            }) == sorted({template.name for template in response.templates})
        )
    
    def test_get_request(self):
        # Doesn't matter whether the user is logged in or not.
        c = Client()
        response = c.get(reverse("index"))
        self.assertEqual(response.context["page"].paginator.count, 2)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(IndexViewTest.check_rendered_templates(response))
        

    def test_valid_authenticated_post_request(self):
        response = IndexViewTest.c.post(reverse("index"), {"body": "test post body"})
        self.assertTrue(Post.objects.filter(body="test post body").exists())
        self.assertEqual(response.status_code, 201)
        self.assertTrue(IndexViewTest.check_rendered_templates(response))

    def test_invalid_authenticated_post_request(self):
        response = IndexViewTest.c.post(reverse("index"), {"body": ""})
        self.assertEqual(response.status_code, 400)
        self.assertTrue(IndexViewTest.check_rendered_templates(response))

    def test_unauthenticated_post_request(self):
        c = Client()
        response = c.post(reverse("index"), {"body": "test post body"})
        self.assertEqual(response.status_code, 401)
        self.assertTrue(IndexViewTest.check_rendered_templates(response))


class PostViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def test_like_post(self):
        response = PostViewTest.c.put(
            reverse("post", args=[PostViewTest.p1.id]), 
            {"liked": True}, 
            content_type="application/json"
        )
        self.assertTrue(response.json()["liked"])
        self.assertEqual(response.json()["like_count"], 1)
        self.assertEqual(response.status_code, 200)

    def test_unlike_post(self):
        PostViewTest.u1.liked_posts.add(PostViewTest.p2)
        PostViewTest.u2.liked_posts.add(PostViewTest.p2)
        response = PostViewTest.c.put(
            reverse("post", args=[PostViewTest.p2.id]), 
            {"liked": False}, 
            content_type="application/json"
        )
        self.assertFalse(response.json()["liked"])
        self.assertEqual(response.json()["like_count"], 1)
        self.assertEqual(response.status_code, 200)

    def test_edit_post_body(self):
        response = PostViewTest.c.put(
            reverse("post", args=[PostViewTest.p1.id]), 
            {"body": "new body"}, 
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 204)

    def test_edit_other_user_post_body(self):
        response = PostViewTest.c.put(
            reverse("post", args=[PostViewTest.p2.id]), 
            {"body": "new body"}, 
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_request(self):
        c = Client()
        response = c.put(
            reverse("post", args=[PostViewTest.p1.id]), 
            {"body": "new body"}, 
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 302)


class UserViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def test_get_request(self):
        response = UserViewTest.c.get(reverse("user", args=[UserViewTest.u2.id]))
        self.assertEqual(response.context["visited_user"], UserViewTest.u2)
        self.assertEqual(response.context["page"].paginator.count, 1)
        self.assertEqual(response.context["is_following"], False)
        self.assertEqual(
            sorted({
                "network/layout.html", 
                "network/profile.html", 
                "network/posts_template.html", 
                "network/user_list_template.html"
            }),
            sorted({template.name for template in response.templates})    
        )

    def test_get_nonexisting_user(self):
        response = UserViewTest.c.get(reverse("user", args=[3]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            sorted(["network/layout.html", "network/404.html"]),
            sorted([template.name for template in response.templates])    
        )

    def test_follow_user(self):
        response = UserViewTest.c.put(reverse("user", args=[UserViewTest.u2.id]))
        self.assertTrue(response.json()["is_following"])
        self.assertEqual(response.json()["follower_count"], 1)

    def test_unfollow_user(self):
        c = Client()
        # Log in as user2 then unfollow user1
        c.login(username="username2", password="password2")
        response = c.put(reverse("user", args=[UserViewTest.u1.id]))
        self.assertFalse(response.json()["is_following"])
        self.assertEqual(response.json()["follower_count"], 0)

    def test_follow_yourself(self):
        response = UserViewTest.c.put(reverse("user", args=[UserViewTest.u1.id]))
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_request(self):
        c = Client()
        response = c.put(reverse("user", args=[UserViewTest.u1.id]))
        self.assertEqual(response.status_code, 401) 


class FollowingViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def test_get_request_without_following_users(self):
        response = FollowingViewTest.c.get(reverse("following"))
        self.assertEqual(response.context["page"].paginator.count, 0)  
        self.assertEqual(
            sorted(["network/layout.html", "network/following.html"]),
            sorted([template.name for template in response.templates])    
        )

    def test_get_request_with_following_users(self):
        FollowingViewTest.u1.following.add(FollowingViewTest.u2)
        response = FollowingViewTest.c.get(reverse("following"))
        self.assertEqual(response.context["page"].paginator.count, 1)
        self.assertEqual(
            sorted(["network/layout.html", "network/following.html", "network/posts_template.html", "network/user_list_template.html"]),
            sorted([template.name for template in response.templates])    
        )

    def test_unauthenticated_request(self):
        c = Client()
        response = c.get(reverse("following"))
        self.assertEqual(response.status_code, 302)


class CommentViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def test_get_nonexisting_comments(self):
        response = CommentViewTest.c.get(reverse("comments", args=[CommentViewTest.p1.id]))
        self.assertEqual(response.json()["comment_count"], 0)
        self.assertEqual(response.json()["page_count"], 1)

    def test_create_comment(self):
        response = CommentViewTest.c.post(
            reverse("comments", args=[CommentViewTest.p1.id]), 
            {"body": "test comment"}, 
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

    def test_get_existing_comments(self):
        response = CommentViewTest.c.get(reverse("comments", args=[CommentViewTest.p2.id]))
        self.assertEqual(len(response.json()["page"]), 1)
        self.assertEqual(response.json()["comment_count"], 1)
        self.assertEqual(response.json()["page_num"], 1)
        self.assertEqual(response.json()["page_count"], 1)


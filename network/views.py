from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from .models import *


def index(request):
    # Create a post.
    if request.method == "POST":
        if request.user.is_authenticated:
            body = request.POST["body"]
            new_post = Post(author=request.user, body=body)
            new_post.save()
            messages.add_message(request, messages.SUCCESS, "Your post has been created.")
        else:
            messages.add_message(request, messages.ERROR, "You need to log in before posting.")    
    
    posts = Post.objects.order_by("-date_created")
    for post in posts:
        setattr(post, "like_count", post.likers.count())
        if request.user.is_authenticated:
            setattr(post, "liked", request.user.liked_posts.filter(pk=post.id).exists())
    page_num = request.GET.get("page")
    if not page_num:
        page_num = 1
    paginator = Paginator(posts, 10)
    page = paginator.get_page(page_num)
    return render(request, "network/index.html", {
        "page": page
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.add_message(request, messages.ERROR,
                                 "Invalid username and/or password.")
            return render(request, "network/login.html")
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.add_message(request, messages.ERROR,
                                 "Passwords must match.")
            return render(request, "network/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR,
                                 "Username already taken.")
            return render(request, "network/register.html")
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# Route for updating a post's likes or body(content). 
@csrf_exempt
@login_required
def post(request, post_id):
    if request.method == "PUT":
        data= json.loads(request.body)
        post = Post.objects.get(pk=post_id)
        if data.get("liked") is not None:
            if data["liked"]:
                request.user.liked_posts.add(post)
            else:
                request.user.liked_posts.remove(post)
            return JsonResponse({
                "like_count": post.likers.count(),
                "liked": request.user.liked_posts.filter(pk=post_id).exists()
            }, status=200)
        elif data.get("body") is not None:
            if post.author != request.user:
                return JsonResponse({
                    "message": "You can't edit another user's post!"
                }, status=403)
            post.body = data["body"]
            post.save()
            return HttpResponse(status=204)


@csrf_exempt
def user(request, user_id):
    # Display a 404 page if user does not exist.
    try:
        visited_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return render(request, "network/404.html", {
            "message": "User not found"
        }, status=404)
    # Follow/unfollow a user.
    if request.method == "PUT":
        if request.user.following.filter(pk=user_id).exists():
            request.user.following.remove(visited_user)
        else:
            request.user.following.add(visited_user)
        return JsonResponse({
            "is_following": request.user.following.filter(pk=user_id).exists(),
            "follower_count": visited_user.followers.count()
        }, status=200)
    # Visit a user's profile page.
    else:
        posts = Post.objects.filter(author=visited_user).order_by("-date_created")
        for post in posts:
            setattr(post, "like_count", post.likers.count())
            if request.user.is_authenticated:
                setattr(post, "liked", request.user.liked_posts.filter(pk=post.id).exists())
        page_num = request.GET.get("page")
        if not page_num:
            page_num = 1
        paginator = Paginator(posts, 10)
        page = paginator.get_page(page_num)
        context = {
            "visited_user": visited_user,
            "follower_count": visited_user.followers.count(),
            "following_count": visited_user.following.count(),
            "page": page
        }
        if request.user.is_authenticated:
            context["is_following"] = request.user.following.filter(id=visited_user.id).exists()
        return render(request, "network/profile.html", context)
    

# Route for viewing the posts of all the users the logged in user follows.
@login_required
def following(request):
    posts = Post.objects.filter(author__in=request.user.following.all()).order_by("-date_created")
    for post in posts:
        setattr(post, "like_count", post.likers.count())
        setattr(post, "liked", request.user.liked_posts.filter(pk=post.id).exists())
    page_num = request.GET.get("page")
    if not page_num:
        page_num = 1
    paginator = Paginator(posts, 10)
    page = paginator.get_page(page_num)
    return render(request, "network/following.html", {
        "page": page
    })


@csrf_exempt
def comments(request, post_id):
    # Create a comment.
    if request.method == "POST":
        body = json.loads(request.body)["body"]
        new_comment = Comment.objects.create(author=request.user, post=Post.objects.get(pk=post_id), body=body)
        return JsonResponse({
            "message": "Comment created successfully",
        }, status=201)
    # Get all specific post's comments.
    else:
        comments = Comment.objects.filter(post=Post.objects.get(pk=post_id)).order_by("-date_created")
        page_num = request.GET.get("page")
        if not page_num:
            page_num = 1
        paginator = Paginator(comments, 5)
        page = paginator.get_page(page_num)
        comment_page = []
        for comment in page.object_list.select_related("author"):
            comment_page.append({
                "author": comment.author.username,
                "body": comment.body,
                "date_created": comment.date_created.strftime("%b. %#d, %Y, %#I:%M %p")
            })
        print(comment_page)
        return JsonResponse({
            "comment_count": paginator.count,
            "page": comment_page,
            "page_num": page.number,
            "page_count": paginator.num_pages
        })
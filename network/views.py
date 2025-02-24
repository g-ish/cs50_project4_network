import json
import pickle

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, NetworkPost, NetworkPostLikeManager
# from .models import NetworkFollowManager

def index(request):
    if request.user.is_authenticated:
        posts = NetworkPost.objects.all().order_by('-timestamp')[:10]
        for post in posts:
            post.likes_count = NetworkPostLikeManager.objects.filter(post=post).count
            if NetworkPostLikeManager.objects.filter(post=post, liked_by=request.user).exists():
                post.liked = True
            else:
                post.liked = False

        return render(request, "network/index.html", {'posts': posts})

    return render(request, "network/index.html")


@csrf_exempt
# Todo: This probably shouldnt be CSRF Exempt
def like_post(request):
    post_id = ''
    try:
        data = json.loads(request.body)
        post_id = data['post_id']

        post = NetworkPost.objects.get(id=post_id)
        if NetworkPostLikeManager.objects.filter(post=post, liked_by=request.user).exists():
            like = NetworkPostLikeManager.objects.get(post=post, liked_by=request.user)
            like.delete()
            status = 'unliked'
        else:
            liked_post = NetworkPostLikeManager(post=post, liked_by=request.user)
            liked_post.save()
            status = "liked"
        likes_count = NetworkPostLikeManager.objects.filter(post=post).count()
        return JsonResponse({"postUpdateStatus": status, 'likes': likes_count})
    except Exception as e:
        print(f"Updating likes on post {post_id} failed due to: ")
        print(e)
        return JsonResponse({"postUpdateStatus": "failed: " + str(e)})


def submit_post(request):
    if request.method != "POST":
        return render(request, "network/index.html")
    else:
        post = NetworkPost(author=request.user, content=request.POST['post-content'])
        try:
            post.save()
            return HttpResponseRedirect(reverse("index"))
        except Exception as e:
            print("error on backend: ")
            print(e)
            return HttpResponseRedirect(reverse("index"))


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile_page(request, profile_id):
    profile_user = User.objects.get(id=profile_id)

    profile = {'user': profile_user,
               'followers' : profile_user.followers.count(),
               'following': profile_user.following.count()}

    return render(request, "network/profile.html", {'profile': profile})

@csrf_exempt
def follow_profile(request, profile_id):

    profile_user = User.objects.get(id=profile_id)
    request.user.following.add(profile_user)
    profile_user.followers.add(request.user)

    #Todo: This is now broken :( only allows for following, no removing - readd that back in

    return JsonResponse({"followStatus": "followed"})


# Todo: Add some error checking here for successful and failed api calls.
@csrf_exempt
def get_follow_stats(request, profile_id):
    '''
    :param request:
    :param profile_id:
    :return: JsonResponse of followers and following
    '''
    profile_user = User.objects.get(id=profile_id)

    followers = profile_user.followers.all()
    followers = list(followers.values_list('id', 'username'))

    following = profile_user.following.all()
    following = list(following.values_list('id', 'username'))

    follower_stats = {
        'followers': followers,
        'following' : following
    }

    return JsonResponse({"follower_stats": follower_stats})



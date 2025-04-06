import json
import pickle
from xml.dom.minidom import ProcessingInstruction

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, NetworkPost, NetworkPostLikeManager
from .models import FollowManager

#  original index without any pagination
# def index(request):
#     if request.user.is_authenticated:
#         posts = NetworkPost.objects.all().order_by('-timestamp')[:10]
#         for post in posts:
#             post.likes_count = NetworkPostLikeManager.objects.filter(post=post).count
#             if NetworkPostLikeManager.objects.filter(post=post, liked_by=request.user).exists():
#                 post.liked = True
#             else:
#                 post.liked = False
#
#         return render(request, "network/index.html", {'posts': posts})
#
#     return render(request, "network/index.html")


def index(request, following_only=None):
    # Backend: https://docs.djangoproject.com/en/4.0/topics/pagination/
    # Frontend: https://getbootstrap.com/docs/4.4/components/pagination/
    if request.user.is_authenticated:
        posts = NetworkPost.objects.all().order_by('-timestamp')

        # this is probably inefficient - it's using a DB query for posts which the user may never even see,
        # need to figure out how to only call the DB on visible posts.
        if following_only == "True":
            following = FollowManager.objects.filter(followers=request.user)
            following_users = [user.user.id for user in following]
            posts = NetworkPost.objects.filter(author__in=following_users).order_by('-timestamp')
        else:
            posts = NetworkPost.objects.all().order_by('-timestamp')

        for post in posts:
            post.likes_count = NetworkPostLikeManager.objects.filter(post=post).count
            if NetworkPostLikeManager.objects.filter(post=post, liked_by=request.user).exists():
                post.liked = True
            else:
                post.liked = False

        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        print(page_obj)
        print(page_obj.number)

        # return render(request, "network/index.html", {'posts': page_object})
        return render(request, "network/index.html", {
            'page_obj': page_obj,
            'page_count': paginator.num_pages,
            'current_page': page_obj.number
        })

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
            follow_manager = FollowManager(user=user)
            follow_manager.save()
        except Exception as e:
            print(e)
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

    try:
        follow_manager = FollowManager.objects.get(user=profile_id)
    except FollowManager.DoesNotExist:
        follow_manager = FollowManager(user=request.user)
        follow_manager.save()

    profile = {'user': profile_user,
               'followers': follow_manager.followers.count(),
               'following': follow_manager.following.count()}

    return render(request, "network/profile.html", {'profile': profile})


@csrf_exempt
def follow_profile(request, profile_id):
    target_profile = User.objects.get(id=profile_id)
    # if the profile is already being followed then remove from each FollowManager object
    try:
        user_follow_manager = FollowManager.objects.get(user=request.user, following=target_profile)
        target_profile_manager = FollowManager.objects.get(user=target_profile, followers=request.user)
        user_follow_manager.following.remove(target_profile)
        target_profile_manager.followers.remove(request.user)
        return JsonResponse({"followStatus": "unfollowed"})

    # create a new followerObject
    except FollowManager.DoesNotExist:
        FollowManager.objects.get(user=request.user).following.add(target_profile)
        FollowManager.objects.get(user=target_profile).followers.add(request.user)
        return JsonResponse({"followStatus": "followed"})

# Todo: Add some error checking here for successful and failed api calls.
@csrf_exempt
def get_follow_stats(request, profile_id):
    '''
    :param request:
    :param profile_id:
    :return: JsonResponse of followers and following

    
    '''
    try:
        follow_manager = FollowManager.objects.get(user=profile_id)
    except FollowManager.DoesNotExist:
        follow_manager = FollowManager(user=request.user)
        follow_manager.save()

    followers = follow_manager.followers.all()
    followers = list(followers.values_list('id', 'username'))

    following = follow_manager.following.all()
    following = list(following.values_list('id', 'username'))

    follower_stats = {
        'followers': followers,
        'following': following
    }

    return JsonResponse({"follower_stats": follower_stats})



# def create_test_cases(request):
#     # This just creates a bunch of test data in the live DB because i can't achieve it through test cases,
#     import random
#
#
#     def create_users():
#         usernames = []
#         for i in range(30):
#             username = 'testUser' + str(i)
#             User.objects.create_user(username=username, email=username + '@test.com', password=username)
#
#             usernames.append((username, i))
#         return usernames
#
#     def create_posts(users):
#         posts = []
#         for user in users:
#             username = user[0]
#             user = User.objects.get(username=username)
#             content = 'This is a test post from user: ' + user.username
#             post = NetworkPost(author=user, content=content)
#             post.save()
#             posts.append((user, post, content))
#         return posts
#
#     def follow_random(users):
#         for user in users:
#             username = user[0]
#             profile_1 = User.objects.get(username=username)
#
#             random_id = random.choice([num for num in range(30) if num != username[1]])
#             profile_2 = users[random_id][0]
#
#             print(f"randomising follow for {profile_1} with {profile_2}")
#
#             rand_follow_selection = random.randint(0, 1)
#
#             profile_2 = User.objects.get(username=profile_2)
#             if rand_follow_selection == 0:
#                 follow_object = FollowManager.objects.get_or_create(user=profile_1)[0]
#                 follow_object.following.add(profile_2)
#                 follow_object.save()
#
#                 follow_object = FollowManager.objects.get_or_create(user=profile_2)[0]
#                 follow_object.followers.add(profile_1)
#                 follow_object.save()
#             else:
#                 follow_object = FollowManager.objects.get_or_create(user=profile_2)[0]
#                 follow_object.followers.add(profile_1)
#                 follow_object.save()
#
#                 follow_object = FollowManager.objects.get_or_create(user=profile_1)[0]
#                 follow_object.followers.add(profile_2)
#                 follow_object.save()
#
#         # hard test
#         profile_a = User.objects.get(username="testUser0")
#         profile_b = User.objects.get(username="testUser1")
#
#         profile_a_following = FollowManager.objects.get_or_create(user=profile_a)[0]
#         profile_a_following.following.add(profile_b)
#
#         profile_b_follower = FollowManager.objects.get_or_create(user=profile_b)[0]
#         profile_b_follower.followers.add(profile_a)
#
#     print("creating users")
#     usernames = create_users()
#
#     print("creating posts")
#     create_posts(usernames)
#     follow_random(usernames)
#
#     return HttpResponseRedirect(index)
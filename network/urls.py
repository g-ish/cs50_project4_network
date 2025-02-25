
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("submit_post", views.submit_post, name="submit_post"),
    path('like_post', views.like_post, name='like_post'),
    path('profile/<int:profile_id>/', views.profile_page, name='profile'),
    path('profile/<int:profile_id>/follow/', views.follow_profile, name='follow_profile'),
    path('profile/<int:profile_id>/get_follow_stats/', views.get_follow_stats, name='get_follow_stats'),
    path('view_following', views.view_following, name='view_following'),
]

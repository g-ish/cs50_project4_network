from django.contrib import admin

from network.models import User, NetworkPost, NetworkPostLikeManager

from network.models import FollowManager

# Register your models here.
admin.site.register(User)
admin.site.register(NetworkPost)
admin.site.register(NetworkPostLikeManager)
admin.site.register(FollowManager)
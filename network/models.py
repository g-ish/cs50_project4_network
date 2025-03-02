from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class FollowManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # followers = models.ForeignKey("User", related_name="followers", null=True, blank=True, on_delete=models.CASCADE)
    # following = models.ForeignKey("User", related_name="following", null=True, blank=True, on_delete=models.CASCADE)
    followers = models.ManyToManyField("User", related_name="followers", null=True, blank=True)
    following = models.ManyToManyField("User", related_name="following", null=True, blank=True)


class NetworkPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)


class NetworkPostLikeManager(models.Model):
    post = models.ForeignKey(NetworkPost, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="liked by")
    class Meta:
        unique_together = ('liked_by', 'post')
        verbose_name = 'likes'

    def __str__(self):
        return f'{self.liked_by}'


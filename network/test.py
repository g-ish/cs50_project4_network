import os
import random

from django.test import TestCase
from network.models import User, FollowManager, NetworkPost, NetworkPostLikeManager

from django.test.client import Client


class PopulateData(TestCase):
    print("running test")

    def create_users(self):
        usernames = []
        for i in range(30):
            username = 'testUser' + str(i)
            User.objects.create_user(username=username, email=username + '@test.com', password=username)

            usernames.append((username, i))
        return usernames

    def create_posts(self, users):
        for user in users:
            username = user[0]
            user = User.objects.get(username=username)
            content = 'This is a test post from user: ' + user.username
            post = NetworkPost(author=user, content=content)
            post.save()

    def follow_random(self, users):
        for user in users:
            username = user[0]
            profile_1 = User.objects.get(username=username)

            random_id = random.choice([num for num in range(30) if num != username[1]])

            print("random_id")
            profile_2 = users[random_id][0]

            print(f"randomising follow for {profile_1} with {profile_2}")

            rand_follow_selection = random.randint(0, 1)

            profile_2 = User.objects.get(username=profile_2)
            if rand_follow_selection == 0:
                follow_object = FollowManager.objects.get_or_create(user=profile_1)[0]
                follow_object.following.add(profile_2)

                follow_object.save()

                follow_object = FollowManager.objects.get_or_create(user=profile_2)[0]
                follow_object.followers.add(profile_1)
                follow_object.save()
            else:
                follow_object = FollowManager.objects.get_or_create(user=profile_2)[0]
                follow_object.followers.add(profile_1)
                follow_object.save()

                follow_object = FollowManager.objects.get_or_create(user=profile_1)[0]
                follow_object.followers.add(profile_2)
                follow_object.save()

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_all(self):
        password = 'admin'
        admin = User.objects.create_superuser('admin', 'admin@test.com', password)
        c = Client()
        c.login(username=admin.username, password=password)
        print("creating users")
        usernames = self.create_users()
        print("creating posts")
        self.create_posts(usernames)
        print("randomising followers/following")
        self.follow_random(usernames)

        input(
            'Execution is paused and you can now inspect the database.\n'
            'Press return/enter key to continue:')


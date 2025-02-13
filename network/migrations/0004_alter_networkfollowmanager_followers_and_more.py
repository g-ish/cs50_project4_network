# Generated by Django 5.1.5 on 2025-01-30 18:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_alter_networkpostlikemanager_liked_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='networkfollowmanager',
            name='followers',
            field=models.ManyToManyField(null=True, related_name='followers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='networkfollowmanager',
            name='following',
            field=models.ManyToManyField(null=True, related_name='following', to=settings.AUTH_USER_MODEL),
        ),
    ]

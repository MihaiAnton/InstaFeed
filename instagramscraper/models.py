from django.db import models


# Instagram data
class Profile(models.Model):
    username = models.TextField(primary_key=True, max_length=256)
    accessible = models.BooleanField(default=True)


class Post(models.Model):
    path = models.TextField(max_length=256)
    description = models.TextField(max_length=1024, default="")
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)


class Image(models.Model):
    url = models.URLField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # TODO add actual image


# Changes data
class Change(models.Model):
    """Defines a change to a profile.
    """
    class ChangeType(models.TextChoices):
        PROFILE_NOT_ACCESSIBLE = 'PROFILE_NOT_ACCESSIBLE'
        POST_ADDED = 'POST_ADDED'
        POST_REMOVED = 'POST_REMOVED'

    profile = models.ForeignKey(Profile)
    change_type = models.CharField(max_length=64, choices=ChangeType.choices)
    post = models.ForeignKey(Post)

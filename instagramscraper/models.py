from django.db import models


# Instagram data
class Profile(models.Model):
    username = models.CharField(primary_key=True, max_length=64)
    accessible = models.BooleanField(default=True)

    def __str__(self):
        access = " | inaccessible" if not self.accessible else ""
        return f"<Profile {self.username}{access}>"

    def __repr__(self):
        return str(self)


class Post(models.Model):
    path = models.TextField(primary_key=True, max_length=256)
    description = models.TextField(max_length=2048, default="")
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    removed = models.BooleanField(default=False)

    def __str__(self):
        return f"<Post {self.description}>"

    def __repr__(self):
        return str(self)


class Image(models.Model):
    url = models.TextField(primary_key=True, max_length=2048)
    post = models.ForeignKey(Post, on_delete=models.PROTECT)

    def __str__(self):
        return f"<Image {self.url}>"

    def __repr__(self):
        return str(self)


# Changes data
class Change(models.Model):
    """Defines a change to a profile.
    """
    class ChangeType(models.TextChoices):
        PROFILE_NOT_ACCESSIBLE = 'PROFILE_NOT_ACCESSIBLE'
        POST_ADDED = 'POST_ADDED'
        POST_REMOVED = 'POST_REMOVED'

    change_type = models.CharField(max_length=64, choices=ChangeType.choices)
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_sent = models.BooleanField(default=False)

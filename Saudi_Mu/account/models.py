from django.db import models
from django.contrib.auth.models import User
from museum.models import Museum


# Create your models here.

# accounts/models.py


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="images/avatars/", default="images/avatars/avatar.webp")
    website_link = models.URLField(blank=True)  # بدل twitch ممكن موقع الهيئة أو المتحف

    def __str__(self):
        return f"Profile {self.user.username}"







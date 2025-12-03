from django.db import models
from django.contrib.auth.models import User


# Create your models here.

# accounts/models.py


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="images/avatars/", default="images/avatars/avatar.webp")
    website_link = models.URLField(blank=True)  # بدل twitch ممكن موقع الهيئة أو المتحف

    def __str__(self):
        return f"Profile {self.user.username}"



class Bookmark(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

class AuthorityProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='authorityprofile')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='authority_logos/', blank=True, null=True)





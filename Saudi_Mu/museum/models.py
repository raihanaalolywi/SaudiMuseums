from django.db import models
from django.contrib.auth.models import User


# مودل أنواع الهيئات (الأدمن هو اللي يضيفها)
class AuthorityType(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


# مودل لاضافة الهيئات 
class Authority(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # ربط الهيئة بنوع الهيئة
    type = models.ForeignKey(
        AuthorityType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to="authority/")
    location = models.CharField(max_length=150)
    map_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name



class Museum(models.Model):
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="museum/")
    location = models.CharField(max_length=150)
    description = models.TextField()

    # ================= NEW FIELDS =================
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    


    # اضفت المودل لاضافة تعليق هنا 

class MuseumComment(models.Model):
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    comment = models.TextField()                     
    rating = models.IntegerField(default=1)         

    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} - {self.museum.name}"


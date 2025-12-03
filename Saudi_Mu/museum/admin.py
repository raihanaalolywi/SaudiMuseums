from django.contrib import admin
from .models import Authority, AuthorityType


admin.site.register(AuthorityType)
admin.site.register(Authority)
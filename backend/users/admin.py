from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.models import Token

from .models import CustomUser

admin.site.register(CustomUser, UserAdmin)

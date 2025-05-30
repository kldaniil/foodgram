from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscriptions, CustomUser


UserAdmin.fieldsets += (
    ('Extra fields', {'fields': ('role',)}),
)

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Subscriptions)

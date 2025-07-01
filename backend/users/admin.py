from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    '''Админка для кастомной модели пользователя.'''
    readonly_fields = ('preview',)

    @admin.display(description='Аватар')
    def preview(self, obj):
        '''Превью аватара пользователя.'''
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px;" />', obj.image.url
            )
        return 'Нет изображения'

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('preview',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)

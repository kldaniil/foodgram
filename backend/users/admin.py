from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html

User = get_user_model()


@admin.register(User)
class ExtendedUserAdmin(UserAdmin):
    """Админка для кастомной модели пользователя."""
    readonly_fields = ('preview',)

    @admin.display(description='Аватар')
    def preview(self, obj):
        """Превью аватара пользователя."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px;" />', obj.image.url
            )
        return 'Нет изображения'

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('preview',)}),
    )


admin.site.unregister(Group)

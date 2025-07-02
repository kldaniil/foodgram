from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (EmailValidator, MaxLengthValidator,
                                    MinLengthValidator, RegexValidator)
from django.db import models

from .constants import (EMAIL_FIELD_MAX_LENGTH, EMAIL_FIELD_MIN_LENGTH,
                        USERNAME_FIELD_MAX_LENGTH, USERNAME_FIELD_MIN_LENGTH)


class ExtendedUser(AbstractUser):
    """Кастомная модель пользователя."""
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=USERNAME_FIELD_MAX_LENGTH,
        validators=[
            MinLengthValidator(USERNAME_FIELD_MIN_LENGTH),
            MaxLengthValidator(USERNAME_FIELD_MAX_LENGTH),
            RegexValidator(regex=r'^[\w.@+-]+\Z', message='Недопустимое имя'),
        ]
    )

    email = models.EmailField(
        unique=True,
        max_length=EMAIL_FIELD_MAX_LENGTH,
        validators=[
            MinLengthValidator(EMAIL_FIELD_MIN_LENGTH),
            MaxLengthValidator(EMAIL_FIELD_MAX_LENGTH),
            EmailValidator(message='Недопустимый email'),
        ]
    )

    first_name = models.CharField(
        'Имя',
        max_length=USERNAME_FIELD_MAX_LENGTH,
        validators=[
            MaxLengthValidator(USERNAME_FIELD_MAX_LENGTH),
            MinLengthValidator(USERNAME_FIELD_MIN_LENGTH),
        ]
    )

    last_name = models.CharField(
        'Фамилия',
        max_length=USERNAME_FIELD_MAX_LENGTH,
        validators=[
            MaxLengthValidator(USERNAME_FIELD_MAX_LENGTH),
            MinLengthValidator(USERNAME_FIELD_MIN_LENGTH),
        ]
    )

    avatar = models.ImageField(
        'Аватар',
        blank=True,
        upload_to='images/',
        null=True,
        default=None
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['-date_joined', 'username']

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Модель для подписок пользователей."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='кто подписан'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='на кого подписан'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_followings'
            ),
            models.CheckConstraint(
                check=~models.Q(user__exact=models.F('following')),
                name='self_subscribe_not_allowed',

            )
        ]
        ordering = ['user', 'following']

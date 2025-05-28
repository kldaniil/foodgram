import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers


User = get_user_model()


class AvatarField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, image_data = data.split(';base64,')
            extension = format.split('/')[-1]
            user_id = self.context['request'].user.id
            data = ContentFile(
                base64.b64decode(image_data),
                name=f'avatar_{user_id}.{extension}'
            )
        return super().to_internal_value(data)

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        'check_subscription',
        read_only=True
    )
    avatar = AvatarField(required=False, allow_null=True)

    def get_avatar(self, obj):
        pass

    def check_subscription(self, obj):
        pass

    class Meta(UserSerializer.Meta):
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        ]


class AvatarSerializer(serializers.ModelSerializer):
    avatar = AvatarField(required=False, allow_null=True)
    class Meta:
        model = User
        fields = ['avatar',]

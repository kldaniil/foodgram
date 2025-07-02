import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class ImageField(serializers.ImageField):
    """Поле для изображений с base64 кодировкой."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            file_format, image_data = data.split(';base64,')
            extension = file_format.split('/')[-1]
            user_id = self.context['request'].user.id
            data = ContentFile(
                base64.b64decode(image_data),
                name=f'image_{user_id}.{extension}'
            )
        return super().to_internal_value(data)

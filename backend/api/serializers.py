import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (
    Favorites, Ingredients, Recipes, RecipesIngredients, ShoppingList, Tags
)
from users.models import Subscriptions


User = get_user_model()


class ImageField(serializers.ImageField):
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
    avatar = serializers.ImageField(required=False, allow_null=True)

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
    avatar = ImageField(required=False, allow_null=True)
    class Meta:
        model = User
        fields = ['avatar',]


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class TagsSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class SubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = '__all__'


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = '__all__'


class IngredientsAmountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class RecipesWriteSerializer(serializers.ModelSerializer):
    image = ImageField()
    ingredients = IngredientsAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset = Tags.objects.all(), many=True
    )
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    def save_ingredients_and_amount(self, recipe, ingredients):
        save_list = []
        for ingredient in ingredients:
            ingredient_object = Ingredients.objects.get(id=ingredient['id'])
            save_list.append(
                RecipesIngredients(
                    recipe=recipe,
                    ingredient=ingredient_object,
                    amount=ingredient['amount']
                )
            )
        RecipesIngredients.objects.bulk_create(save_list)

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        ingredients = validated_data.pop('ingredients')
        print("ingredients in create:", ingredients)
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.save_ingredients_and_amount(recipe, ingredients)
        return recipe
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        print("ingredients in update:", ingredients)
        tags = validated_data.pop('tags')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        instance.tags.set(tags)
        RecipesIngredients.objects.filter(recipe=instance).delete()
        self.save_ingredients_and_amount(instance, ingredients)
        return instance
    
    def to_representation(self, instance):
        read_serializer = RecipesReadSerializer(instance, context=self.context)
        return read_serializer.data

    class Meta:
        model = Recipes
        fields = '__all__'


class RecipesReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    tags = TagsSerialiser(many=True)
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients_list = []
        for item in obj.recipe_ingredients.all():
            ingredients_list.append(
                {
                    'id': item.ingredient.id,
                    'name': item.ingredient.name,
                    'measurement_unit': item.ingredient.measurement_unit,
                    'amount': item.amount,
                }
            )
        return ingredients_list

    class Meta:
        model = Recipes
        fields = '__all__'

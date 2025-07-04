from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredients, Recipes, RecipesIngredients, Tags

from .fields import ImageField
from .validators import ingredients_validator, tags_validator

User = get_user_model()


class ExtendedUserSerializer(UserSerializer):
    """Кастомный сериализатор для пользователя с дополнительными полями."""
    is_subscribed = serializers.SerializerMethodField('check_subscription',)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        ]

    def check_subscription(self, obj):
        """Проверяет, подписан ли пользователь на данного автора."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.followers.filter(user=request.user).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор обновления аватара."""
    avatar = ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ['avatar', ]

    def validate_avatar(self, value):
        """Проверяет, что аватар не пуст."""
        if not value:
            raise serializers.ValidationError('Аватар отсутствует.')
        return value


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredients
        fields = '__all__'


class TagsSerialiser(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов с количеством для чтения."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredients.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipesIngredients
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeFavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Recipes
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецептов."""
    image = ImageField()
    ingredients = IngredientsAmountSerializer(
        many=True,
        required=True,
        allow_empty=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True,
        required=True,
        allow_empty=False,
        validators=(tags_validator,)
    )

    class Meta:
        model = Recipes
        fields = (
            'name', 'text', 'image', 'cooking_time',
            'tags', 'ingredients'
        )

    def validate(self, attrs):
        ingredients_validator(attrs.get('ingredients'))
        tags_validator(attrs.get('tags'))
        return attrs

    def save_ingredients_and_amount(self, recipe, ingredients):
        """Сохраняет ингредиенты и их количество."""
        save_list = []
        for ingredient in ingredients:
            ingredient_object = ingredient['ingredient']
            save_list.append(
                RecipesIngredients(
                    recipe=recipe,
                    ingredient=ingredient_object,
                    amount=ingredient['amount']
                )
            )
        RecipesIngredients.objects.bulk_create(save_list)

    @transaction.atomic
    def create(self, validated_data):
        """Создает рецепт."""
        request = self.context.get('request')
        validated_data['author'] = request.user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.save_ingredients_and_amount(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.save_ingredients_and_amount(instance, ingredients)
        return instance

    def to_representation(self, instance):
        """Преобразует объект в словарь."""
        read_serializer = RecipesReadSerializer(instance, context=self.context)
        return read_serializer.data


class RecipesReadSerializer(RecipeFavoritesSerializer):
    """Сериализатор для чтения рецептов."""
    author = ExtendedUserSerializer()
    tags = TagsSerialiser(many=True)
    ingredients = IngredientsAmountSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False
    )

    class Meta:
        model = Recipes
        exclude = ('short_link', 'created_at')


class SubscriptionsSerializer(ExtendedUserSerializer):
    """Сериализатор подписок."""
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'avatar', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        """Получает рецепты пользователя."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get(
            'recipes_limit', settings.DEFAULT_PAGE_SIZE
        )
        recipes = obj.recipes.all()[:int(recipes_limit)]
        serializer = RecipeFavoritesSerializer(
            recipes,
            read_only=True,
            many=True,
            context=self.context
        )
        return serializer.data

    def get_recipes_count(self, obj):
        """Считает количество рецептов пользователя."""
        return obj.recipes.count()

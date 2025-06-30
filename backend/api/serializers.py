import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (
    Favorites, Ingredients, MIN_POSITIVE_VALUE, Recipes,
    RecipesIngredients, ShoppingList, Tags
)

from .pagination import DEFAULT_PAGE_SIZE
from .validators import ingredients_validator, tags_validator


User = get_user_model()


class ImageField(serializers.ImageField):
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


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'username', 'email', 'password'
        ]


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        'check_subscription',
        read_only=True
    )
    avatar = serializers.ImageField(required=False, allow_null=True)

    def check_subscription(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.followers.filter(user=user).exists()

    class Meta(UserSerializer.Meta):
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        ]


class AvatarSerializer(serializers.ModelSerializer):
    avatar = ImageField(required=True, allow_null=False)

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


class IngredientsAmountWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(MinValueValidator(MIN_POSITIVE_VALUE),)
    )


class IngredientsAmountReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipesIngredients
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeFavoritesSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipes
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipesWriteSerializer(serializers.ModelSerializer):
    image = ImageField()
    ingredients = IngredientsAmountWriteSerializer(
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
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate_ingredients(self, value):
        return ingredients_validator(value)
    
    def validate_tags(self, value):
        return tags_validator(value)

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
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.save_ingredients_and_amount(recipe, ingredients)
        return recipe
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags is None:
            raise serializers.ValidationError(
                {'tags': 'Поле tags обязательно'}
            )
        if ingredients is None:
            raise serializers.ValidationError(
                {'ingredients': 'Поле ingredients обязательно'}
            )
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


class RecipesReadSerializer(RecipeFavoritesSerializer):
    author = CustomUserSerializer()
    tags = TagsSerialiser(many=True)
    ingredients = IngredientsAmountReadSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def make_bool_field(self, obj, model):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and model.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return self.make_bool_field(obj, ShoppingList)

    def get_is_favorited(self, obj):
        return self.make_bool_field(obj, Favorites)

    class Meta:
        model = Recipes
        fields = '__all__'


class SubscriptionsSerializer(CustomUserSerializer):
    # recipes = RecipeFavoritesSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get(
            'recipes_limit', DEFAULT_PAGE_SIZE
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
        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'avatar', 'recipes', 'recipes_count'
        )


# TODO привести поля в порядок. Разобраться с возможно лишними сериалайзерами


class ShortLinkSerializer(serializers.ModelSerializer):
    short_link = serializers.SerializerMethodField()

    def get_short_link(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        site_url = request.scheme + '://' + request.get_host().split(':')[0]
        short_link = site_url + '/s/' + obj.link
        return short_link
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['short-link'] = data.pop('short_link')
        return data

    class Meta:
        model = Recipes
        fields = ('short_link',)


from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator

from .constants import (MAX_INGREDIENT_MEASURE_LENGTH,
                        MAX_INGREDIENT_NAME_LENGTH, MAX_LINK_LENGTH,
                        MAX_POSITIVE_VALUE, MAX_RECIPE_LENGTH, MAX_TAG_LENGTH,
                        MIN_POSITIVE_VALUE, SHORT_STRING)


class Tags(models.Model):
    """Модель для тегов."""
    name = models.CharField('Тег', max_length=MAX_TAG_LENGTH, unique=True)
    slug = models.SlugField('Slug', max_length=MAX_TAG_LENGTH, unique=True)

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return Truncator(self.name).chars(SHORT_STRING)


class Ingredients(models.Model):
    """Модель для ингредиентов."""
    name = models.CharField('Название', max_length=MAX_INGREDIENT_NAME_LENGTH)
    measurement_unit = models.CharField(
        'Единицы измерения', max_length=MAX_INGREDIENT_MEASURE_LENGTH
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_unit'
            )
        ]

    def __str__(self):
        return (
            f'{Truncator(self.name).chars(SHORT_STRING)} '
            f'({self.measurement_unit})'
        )


class Recipes(models.Model):
    """Модель для рецептов."""
    name = models.CharField('Название', max_length=MAX_RECIPE_LENGTH)
    text = models.TextField('Содержание')
    image = models.ImageField(
        'Фото блюда',
        upload_to='images/',
        blank=True,
        null=True,
        default=None
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(MIN_POSITIVE_VALUE),
            MaxValueValidator(MAX_POSITIVE_VALUE)
        ]
    )
    tags = models.ManyToManyField(Tags, related_name='recipes', blank=True)
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipesIngredients',
        related_name='recipes'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    short_link = models.CharField(
        'Короткая ссылка',
        max_length=MAX_LINK_LENGTH,
        unique=True,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-created_at', 'name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return Truncator(self.name).chars(SHORT_STRING)


class RecipesIngredients(models.Model):
    """Модель для связи рецептов и ингредиентов."""
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(MIN_POSITIVE_VALUE),
            MaxValueValidator(MAX_POSITIVE_VALUE)
        ]
    )

    class Meta:
        ordering = ['recipe', 'ingredient']
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'


class BaseUserRecipeModel(models.Model):
    """Абстрактная модель для избранного и списка покупок."""
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        ordering = ['user', 'recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_user_recipe'
            )
        ]


class Favorites(BaseUserRecipeModel):
    """Модель для избранных рецептов пользователя."""
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorites_recipes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_favorites_recipes'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранные'


class ShoppingList(BaseUserRecipeModel):
    """Модель для списка покупок пользователя."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_shopping_list'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipes_user_shopping_list'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

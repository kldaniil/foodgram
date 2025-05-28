from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


MAX_TAG_LENGTH = 32
MAX_RECIPE_LENGTH = 256
MAX_INGREDIENT_NAME_LENGTH = 128
MAX_INGREDIENT_MEASURE_LENGTH = 32


class Tags(models.Model):
    name = models.CharField('Тег', max_length=MAX_TAG_LENGTH)
    slug = models.SlugField('Slug', max_length=MAX_TAG_LENGTH, unique=True)
    class Meta:
        ordering = ['id',]
        verbose_name = 'Tag'
        verbose_name_plural = 'tags'


class Ingredients(models.Model):
    name = models.CharField('Название', max_length=MAX_INGREDIENT_NAME_LENGTH)
    measurement_unit = models.CharField(
        'Единицы измерения', MAX_INGREDIENT_MEASURE_LENGTH
    )
    class Meta:
        ordering = ['id',]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'ингредиенты'


class Recipes(models.Model):
    name = models.CharField('Название', max_length=MAX_RECIPE_LENGTH)
    text = models.TextField('Содержание')
    image = models.ImageField(
        'Фото блюда',
        upload_to='images/',
        blank=True,
        null=True,
        default=None
    )
    cooking_time = models.PositiveSmallIntegerField('Время приготовления'),
    tags = models.ManyToManyField(Tags, related_name='Recipes')
    ingredients = models.ManyToManyField(
        'Ингредиенты',
        through='RecipesIngredients',
    )
    class Meta:
        ordering = ['id',]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'


class RecipesIngredients(models.Model):
    recipes = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField('Количество')
    class Meta:
        ordering = ['id',]
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

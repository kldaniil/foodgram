from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import Truncator

SHORT_STRING = 25
MAX_TAG_LENGTH = 32
MAX_RECIPE_LENGTH = 256
MAX_INGREDIENT_NAME_LENGTH = 128
MAX_INGREDIENT_MEASURE_LENGTH = 32
MIN_POSITIVE_VALUE = 1
MAX_LINK_LENGTH = 32


class Tags(models.Model):
    name = models.CharField('Тег', max_length=MAX_TAG_LENGTH)
    slug = models.SlugField('Slug', max_length=MAX_TAG_LENGTH, unique=True)

    class Meta:
        ordering = ['id',]
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return Truncator(self.name).chars(SHORT_STRING)


class Ingredients(models.Model):
    name = models.CharField('Название', max_length=MAX_INGREDIENT_NAME_LENGTH)
    measurement_unit = models.CharField(
        'Единицы измерения', max_length=MAX_INGREDIENT_MEASURE_LENGTH
    )

    class Meta:
        ordering = ['id',]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return Truncator(self.name).chars(SHORT_STRING)


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
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(MIN_POSITIVE_VALUE),]
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

    class Meta:
        ordering = ['id',]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return Truncator(self.name).chars(SHORT_STRING)


class RecipesIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(MIN_POSITIVE_VALUE)]
    )

    class Meta:
        ordering = ['id',]
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'


class Favorites(models.Model):
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
        ordering = ['id',]
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранные'


class ShoppingList(models.Model):
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
        ordering = ['id',]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Links(models.Model):
    recipe = models.OneToOneField(
        Recipes,
        on_delete=models.CASCADE,
        related_name='short_link'
    )
    link = models.CharField('ссылка', max_length=MAX_LINK_LENGTH)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'link'],
                name='Recipe unique link'
            )
        ]
        ordering = ['id',]
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'короткие ссылки'

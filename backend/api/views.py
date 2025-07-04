import io

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import exceptions, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Favorites, Ingredients, Recipes, ShoppingList, Tags
from users.models import Subscriptions

from .filters import IngredientsFilter, RecipesFilter
from .pagination import RecipesPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, ExtendedUserSerializer,
                          IngredientsSerializer, RecipeFavoritesSerializer,
                          RecipesReadSerializer, RecipesWriteSerializer,
                          SubscriptionsSerializer, TagsSerialiser)

PDF_START_X = 40
PDF_START_Y = 800
PDF_FONT = 'Carlito'
PDF_FONT_SIZE = 14
PDF_HEADER_FONT_SIZE = 18

User = get_user_model()


class IngrediensViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""
    permission_classes = (permissions.AllowAny,)
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter
    queryset = Ingredients.objects.all()


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""
    permission_classes = (permissions.AllowAny,)
    queryset = Tags.objects.all()
    serializer_class = TagsSerialiser
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = RecipesPagination

    def get_queryset(self):
        """Получаем кварисет с аннотированными полями."""
        user = self.request.user
        return Recipes.objects.cart_and_favorites(user)

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecipesWriteSerializer
        return RecipesReadSerializer

    def add_recipe_to_cart_or_favorites(self, request, model):
        """Добавляет рецепт в список покупок или избранное."""
        recipe = self.get_object()
        _, created = model.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(
            RecipeFavoritesSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def delete_recipe_from_cart_or_favorites(self, request, model):
        """Удаляет рецепт из списка покупок или избранного."""
        recipe = self.get_object()
        deleted_count, _ = (
            model.objects
            .filter(user=request.user, recipe=recipe)
            .delete()
        )
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post'],
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавляет в избранное."""
        return self.add_recipe_to_cart_or_favorites(request, Favorites)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удаляет из избранного."""
        return self.delete_recipe_from_cart_or_favorites(request, Favorites)

    @action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок."""
        return self.add_recipe_to_cart_or_favorites(request, ShoppingList)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удаляет рецепт из списка покупок."""
        return self.delete_recipe_from_cart_or_favorites(request, ShoppingList)

    def get_pdf(self, ingredients):
        """Создает PDF-файл со списком покупок."""
        x = PDF_START_X
        y = PDF_START_Y
        font_path = str(
            settings.BASE_DIR / 'fonts' / 'Carlito-Regular.ttf'
        )
        pdfmetrics.registerFont(TTFont(PDF_FONT, font_path))
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setTitle('Мой список покупок')
        pdf.setFont(PDF_FONT, PDF_HEADER_FONT_SIZE)
        pdf.drawString(x, y, 'Список покупок:')
        y -= 10  # отступ от заголовка
        pdf.setFont(PDF_FONT, PDF_FONT_SIZE)
        for item in ingredients:
            y -= 20
            pdf.drawString(
                x, y,
                f'- {item["name"]} {item["amount"]} {item["measurement_unit"]}'
            )

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer

    @action(detail=False, methods=['get', ], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        """Создает PDF-файл со списком покупок."""
        user = request.user
        ingredients = Ingredients.objects.filter(
            ingredients_recipe__recipe__shoppinglist_recipes__user=user
        ).values('name', 'measurement_unit').annotate(
            amount=Sum('ingredients_recipe__amount')
        ).order_by('name',)

        response = HttpResponse(
            self.get_pdf(ingredients),
            content_type='application/pdf;'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"'
        )
        return response

    @action(detail=True, methods=['get', ], url_path='get-link')
    def get_link(self, request, pk=None):
        """Отдает короткую ссылку на рецепт или создает, если ее нет."""
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/s/{recipe.short_link}')

        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


class ExtendedUsersViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""
    serializer_class = ExtendedUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = RecipesPagination
    queryset = User.objects.all()

    def get_permissions(self):
        """Возвращает разрешения в зависимости от действия."""
        if self.action in ['list', 'retrieve']:
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=['get'],
        url_path='me/avatar',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request):
        """Экшн для получения аватара пользователя."""
        user = self.request.user
        serializer = AvatarSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаляет аватар пользователя."""
        user = self.request.user
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @avatar.mapping.put
    def update_avatar(self, request):
        """Обновляет аватар пользователя."""
        user = self.request.user
        if user.avatar:
            user.avatar.delete(save=False)

        serializer = AvatarSerializer(
            user,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=['get'],
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Возвращает информацию о текущем пользователе."""
        return Response(self.get_serializer(request.user).data)

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """Подписка на пользователя."""
        user = request.user
        try:
            subscribe = User.objects.get(id=id)
        except User.DoesNotExist:
            raise exceptions.NotFound('Пользователь не существует')

        if subscribe == user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        _, created = Subscriptions.objects.get_or_create(
            user=user,
            following=subscribe
        )
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(
            SubscriptionsSerializer(
                subscribe, context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Отписка от пользователя."""
        user = request.user
        try:
            subscribe = User.objects.get(id=id)
        except User.DoesNotExist:
            raise exceptions.NotFound('Пользователь не существует')
        if (
            not Subscriptions.objects
            .filter(user=user, following=subscribe)
            .exists()
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscription_count, _ = (
            Subscriptions.objects
            .filter(user=user, following=subscribe)
            .delete()
        )
        if subscription_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=['get', ],
        url_path='subscriptions',
        permission_classes=(permissions.AllowAny,)
    )
    def subscriptions(self, request):
        """Возвращает список подписок пользователя."""

        user = request.user
        queryset = User.objects.filter(followers__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

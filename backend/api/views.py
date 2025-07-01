import io

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorites, Ingredients, Links, Recipes,
                            ShoppingList, Tags)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import exceptions, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscriptions

from .filters import IngredientsFilter, RecipesFilter
from .pagination import CustomPagination
from .permissions import AuthorOrReadOnly
from .serializers import (AvatarSerializer, CustomUserSerializer,
                          IngredientsSerializer, RecipeFavoritesSerializer,
                          RecipesReadSerializer, RecipesWriteSerializer,
                          ShortLinkSerializer, SubscriptionsSerializer,
                          TagsSerialiser)
from .utils import generate_short_link

PDF_START_X = 40
PDF_START_Y = 800
PDF_FONT = 'Carlito'
PDF_FONT_SIZE = 14
PDF_HEADER_FONT_SIZE = 18

User = get_user_model()


class AvatarViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    '''Вьюсет для работы с аватаром пользователя.'''
    serializer_class = AvatarSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        '''Получает текущего пользователя.'''
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        '''Удаляет аватар пользователя.'''
        user = self.get_object()
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        '''Обновляет аватар пользователя.'''
        user = self.get_object()
        if user.avatar:
            user.avatar.delete(save=False)
        return super().update(request, *args, **kwargs)


class IngrediensViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет для работы с ингредиентами.'''
    permission_classes = (permissions.AllowAny,)
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter
    queryset = Ingredients.objects.all()


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет для работы с тегами.'''
    permission_classes = (permissions.AllowAny,)
    queryset = Tags.objects.all()
    serializer_class = TagsSerialiser
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    '''Вьюсет для работы с рецептами.'''
    queryset = Recipes.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        '''Возвращает сериализатор в зависимости от действия.'''
        if self.action in ['create', 'update', 'partial_update']:
            return RecipesWriteSerializer
        return RecipesReadSerializer

    def add_recipe_to_cart_or_favorites(self, request, model):
        '''Добавляет рецепт в список покупок или избранное.'''
        recipe = self.get_object()
        if request.method == 'POST':
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
        elif request.method == 'DELETE':
            if (
                not model.objects
                .filter(user=request.user, recipe=recipe)
                .exists()
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)

            model.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        '''Добавляет или удаляет рецепт из избранного.'''
        return self.add_recipe_to_cart_or_favorites(request, Favorites)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        '''Добавляет или удаляет рецепт из списка покупок.'''
        return self.add_recipe_to_cart_or_favorites(request, ShoppingList)

    @action(detail=False, methods=['get',], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        '''Создает PDF-файл со списком покупок.'''
        user = request.user
        ingredients = Ingredients.objects.filter(
            ingredients_recipe__recipe__recipes_user_shopping_list__user=user
        ).values('name', 'measurement_unit').annotate(
            amount=Sum('ingredients_recipe__amount')
        ).order_by('name',)

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

        response = HttpResponse(
            buffer,
            content_type='application/pdf;'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"'
        )
        return response

    @action(detail=True, methods=['get',], url_path='get-link')
    def get_link(self, request, pk=None):
        '''Создает короткую ссылку на рецепт.'''
        recipe = self.get_object()
        link, _ = Links.objects.get_or_create(
            recipe=recipe,
            defaults={'link': generate_short_link()}
        )
        serializer = ShortLinkSerializer(link, context={'request': request})
        return Response(serializer.data)


class ShortLinkRedirectViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет редиректа по короткой ссылке.'''
    queryset = Links.objects.all()
    lookup_field = 'link'

    def retrieve(self, request, *args, **kwargs):
        '''Перенаправляет по короткой ссылке.'''
        obj = self.get_object()
        url = f'/recipes/{obj.recipe.id}/'
        return redirect(url)


class CustomUsersViewSet(UserViewSet):
    '''Вьюсет для работы с пользователями.'''
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    queryset = User.objects.all()

    def get_permissions(self):
        '''Возвращает разрешения в зависимости от действия.'''
        if self.action in ['list', 'retrieve']:
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()

    @action(
        detail=False, methods=['get'],
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        '''Возвращает информацию о текущем пользователе.'''
        return Response(self.get_serializer(request.user).data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        '''Подписка на пользователя.'''
        user = request.user
        try:
            subscribe = User.objects.get(id=id)
        except User.DoesNotExist:
            raise exceptions.NotFound('Пользователь не существует')

        if request.method == 'POST':
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
        elif request.method == 'DELETE':
            if (
                not Subscriptions.objects
                .filter(user=user, following=subscribe)
                .exists()
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)

            Subscriptions.objects.filter(
                user=user, following=subscribe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get',],
        url_path='subscriptions',
        permission_classes=(permissions.AllowAny,)
    )
    def subscriptions(self, request):
        '''Возвращает список подписок пользователя.'''

        user = request.user
        queryset = User.objects.filter(followers__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

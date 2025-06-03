from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework import (
    exceptions, filters, generics, mixins, permissions, status, viewsets
)
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (
    Favorites, Ingredients, Recipes, RecipesIngredients, ShoppingList, Tags
)
from users.models import Subscriptions

from .filters import IngredientsFilter, RecipesFilter
from .pagination import CustomPagination
from .serializers import (
    AvatarSerializer, IngredientsSerializer, CustomUserSerializer,
    RecipeFavoritesSerializer,
    RecipesReadSerializer, RecipesWriteSerializer, SubscriptionsSerializer,
    TagsSerialiser,
    )

User = get_user_model()


class AvatarViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = AvatarSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def destroy(self, request, *args, **kwargs):
        user = request.user
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
        return super().update(request, *args, **kwargs)


class IngrediensViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter
    queryset = Ingredients.objects.all()
 

class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerialiser
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipesWriteSerializer
        return RecipesReadSerializer
    
    def add_recipe_to_cart_or_favorites(self, request, model):
        recipe = self.get_object()
        if request.method == 'POST':
            model.objects.get_or_create(user=request.user, recipe=recipe)
            return Response(
                RecipeFavoritesSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            model.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        return self.add_recipe_to_cart_or_favorites(request, Favorites)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, requst, pk=None):
        return self.add_recipe_to_cart_or_favorites(requst, ShoppingList)
    
    @action(detail=False, methods=['get',], url_path='download_shopping_cart')
    def download_shopping_cart(self, requset):
        user = requset.user
        ingredients = Ingredients.objects.filter(
            ingredients_recipe__recipe__recipes_user_shopping_list__user=user
        ).values('name', 'measurement_unit').annotate(
            amount=Sum('ingredients_recipe__amount')
        ).order_by('name',)
        shopping_list = []
        for list_item in ingredients:
            shopping_list.append(f'{list_item["name"]}: {list_item["measurement_unitamount"]} {list_item[""]} \n')
        # shopping_list = IngredientsSerializer(ingredients).data
        response = HttpResponse(
            shopping_list,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposotion'] = 'attachment; filename="shopping_cart"'
        return response


class CustomUsersViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = CustomPagination
    queryset = User.objects.all()


    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None, **kwargs):
        user = request.user
        subscribe = User.objects.get(id=id)
        if request.method == 'POST':
            Subscriptions.objects.get_or_create(user=user, following=subscribe)
            return Response(
                CustomUserSerializer(subscribe).data,
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
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
        
        user = request.user
        queryset = User.objects.filter(followers__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


# class SubscriptionsViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = CustomUserSerializer
#     permission_classes = (permissions.IsAuthenticated,)

#     def get_queryset(self):
#         print('!!!!!!!!!!!!!!SUBSCRIPTIONS METHOD CALLED')
#         return User.objects.filter(followers__user=self.request.user)
    # @action(
    #         detail=False, methods=['get',],
    #         url_path='subscriptions',
    #         permission_classes=(permissions.AllowAny,)
    #     )
    # def subscriptions(self, request):
    #     print('!!!!!!!!!!!!!!SUBSCRIPTIONS METHOD CALLED')
    #     user = request.user
    #     queryset = User.objects.filter(followers__user=user)
    #     return Response(
    #         SubscriptionsSerializer(queryset, many=True).data,
    #         status=status.HTTP_200_OK
    #     )

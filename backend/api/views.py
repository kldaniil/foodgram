from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
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


class SubscriptionsViewSet(viewsets.ModelViewSet):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionsSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipesWriteSerializer
        return RecipesReadSerializer
    
    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            Favorites.objects.get_or_create(user=request.user, recipe=recipe)
            return Response(
                RecipeFavoritesSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            Favorites.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


# class UsersRecipesViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = CustomUserSerializer

#     @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
#     def subscribe(self, request, pk=None):
#         user = request.user
#         subscribe = User.objects.get(id=pk)
#         if self.method == 'POST':
#             Subscriptions.objects.get_or_create(user=user, following=subscribe)
#             return Response(
#                 CustomUserSerializer(subscribe),
#                 status=status.HTTP_201_CREATED
#             )
#         elif request.method == 'DELETE':
#             Subscriptions.objects.filter(
#                 user=user, following=subscribe
#             ).delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
class UsersRecipesViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        user = request.user
        subscribe = User.objects.get(id=pk)
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

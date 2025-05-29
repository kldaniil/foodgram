from django.contrib.auth import get_user_model
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import render
from rest_framework import (
    exceptions, filters, generics, mixins, permissions, status, viewsets
)
from rest_framework.response import Response

from recipes.models import (
    Favorites, Ingredients, Recipes, RecipesIngredients, ShoppingList, Tags
)
from users.models import Follow

from .filters import IngredientSearchFilter
from .serializers import (
    AvatarSerializer, IngredientsSerializer, CustomUserSerializer
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
    # filter_backends = (IngredientSearchFilter,)
    # search_fields = ('name',)
    def get_queryset(self):
        queryset = Ingredients.objects.all()

        search = self.request.query_params.get('name')
        if search:
            queryset = queryset.filter(
                name__icontains=search
            ).annotate(
                priority=Case(
                    When(name__istartswith=search, then=Value(0)),
                    When(
                        Q(name__icontains=search)
                        & ~Q(name__istartswith=search),
                        then=Value(1)
                        ),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('priority', 'name')
        return queryset

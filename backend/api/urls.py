from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'api'
router = SimpleRouter()

router.register('users',
                views.DjoserUserViewSet, basename='users')
router.register('tags',
                views.TagsViewSet, basename='tags')
router.register('recipes',
                views.RecipesViewsSet, basename='recipes')
router.register('ingredients',
                views.IngredientsViewsSet, basename='ingredients')
urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
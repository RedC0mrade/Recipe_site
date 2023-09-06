from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()

router.register('users', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
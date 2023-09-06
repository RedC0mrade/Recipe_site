from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'api'
router = SimpleRouter()

router.register('users', views.MyUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
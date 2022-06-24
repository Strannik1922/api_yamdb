from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router_v1 = DefaultRouter()
router_v1.register('users', views.UserViewSet, basename='users')
router_v1.register('posts', views.TitleViewSet, basename='titles')
router_v1.register('posts', views.GenreViewSet, basename='genres')
router_v1.register('posts', views.CategoryViewSet, basename='categories')
# В роутере можно зарегистрировать любое количество пар "URL, viewset":
# например
# router.register('owners', OwnerViewSet)
# Но нам это пока не нужно

urlpatterns = [
    # Все зарегистрированные в router пути доступны в router.urls
    # Включим их в головной urls.py
    path('v1/', include(router_v1.urls)),
]

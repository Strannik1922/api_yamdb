from rest_framework.routers import DefaultRouter

from django.urls import include, path

from . import views


router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')
# В роутере можно зарегистрировать любое количество пар "URL, viewset":
# например
# router.register('owners', OwnerViewSet)
# Но нам это пока не нужно

urlpatterns = [
    # Все зарегистрированные в router пути доступны в router.urls
    # Включим их в головной urls.py
    path('v1/', include(router.urls)),
]

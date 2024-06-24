from rest_framework import routers
from django.urls import path, include
from.views import ReviewViewSet

router = routers.DefaultRouter()
router.register(r'products/(?P<product_id>\d+)/reviews', ReviewViewSet, basename='product-review')
router.register(r'articles/(?P<article_id>\d+)/reviews', ReviewViewSet, basename='article-review')

urlpatterns = [
    path('', include(router.urls)),
]
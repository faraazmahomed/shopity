from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import StoreViewSet, ProductViewSet, ProductReviewViewSet

router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='api-stores')
router.register(r'products', ProductViewSet, basename='api-products')

urlpatterns = [
    path('', include(router.urls)),
    path('products/<int:product_pk>/reviews/', ProductReviewViewSet.as_view({'get': 'list'}), name='api-product-reviews'),
]

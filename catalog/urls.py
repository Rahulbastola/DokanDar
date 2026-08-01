from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductReviewCreateView, ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('products/<int:pk>/reviews/', ProductReviewCreateView.as_view(), name='product-review-create'),
    path('', include(router.urls)),
]

from django.db.models import Avg, Count
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from config.permissions import IsOwnerVendorOrSuperAdminOrReadOnly, IsSuperAdmin
from orders.models import OrderItem

from .filters import ProductFilter
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ReviewSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsSuperAdmin()]


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerVendorOrSuperAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'avg_rating']

    def get_queryset(self):
        qs = Product.objects.select_related('category', 'created_by').prefetch_related('images', 'reviews')
        qs = qs.annotate(avg_rating=Avg('reviews__rating'), review_count=Count('reviews'))

        if self.request.method == 'GET':
            user = self.request.user
            vendor_param = self.request.query_params.get('vendor')
            is_own_products_view = (
                user.is_authenticated
                and vendor_param
                and (str(user.id) == vendor_param or user.is_super_admin)
            )
            if not is_own_products_view:
                qs = qs.filter(is_active=True)

            min_rating = self.request.query_params.get('min_rating')
            if min_rating:
                qs = qs.filter(avg_rating__gte=float(min_rating))

            sort = self.request.query_params.get('sort')
            sort_map = {
                'price_asc': 'price',
                'price_desc': '-price',
                'newest': '-created_at',
                'rating': '-avg_rating',
            }
            qs = qs.order_by(sort_map.get(sort, '-created_at'))
        else:
            user = self.request.user
            if user.is_authenticated and not user.is_super_admin:
                qs = qs.filter(created_by=user)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.is_vendor and user.is_approved) and not user.is_super_admin:
            raise PermissionDenied('Only approved vendors can create products.')
        serializer.save()


class ProductReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.kwargs['pk']
        user = self.request.user

        purchased = OrderItem.objects.filter(
            order__user=user,
            product_id=product_id,
            order__status__in=['paid', 'shipped', 'delivered'],
        ).exists()
        if not purchased:
            raise ValidationError('You can only review products you have purchased.')

        if Review.objects.filter(product_id=product_id, user=user).exists():
            raise ValidationError('You have already reviewed this product.')

        serializer.save(product_id=product_id, user=user)

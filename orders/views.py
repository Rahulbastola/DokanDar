from django.db import transaction
from django.db.models import Count, Sum
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import IsSuperAdmin
from payments.esewa import build_payment_form_fields
from payments.models import Payment
from users.models import User

from .models import Cart, CartItem, Order, OrderItem
from .serializers import AddToCartSerializer, CartSerializer, OrderSerializer


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = _get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        cart = _get_or_create_cart(request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=['quantity'])

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_item(self, request, pk):
        return CartItem.objects.get(pk=pk, cart__user=request.user)

    def patch(self, request, pk):
        try:
            item = self._get_item(request, pk)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)
        quantity = request.data.get('quantity')
        if not quantity or int(quantity) < 1:
            return Response({'detail': 'quantity must be at least 1.'}, status=status.HTTP_400_BAD_REQUEST)
        item.quantity = int(quantity)
        item.save(update_fields=['quantity'])
        return Response(CartSerializer(item.cart).data)

    def delete(self, request, pk):
        try:
            item = self._get_item(request, pk)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)
        cart = item.cart
        item.delete()
        return Response(CartSerializer(cart).data)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart = _get_or_create_cart(request.user)
        items = list(cart.items.select_related('product').select_for_update())
        if not items:
            raise ValidationError('Your cart is empty.')

        for item in items:
            if item.quantity > item.product.stock:
                raise ValidationError(f'Not enough stock for {item.product.name}.')

        total_amount = sum(item.product.price * item.quantity for item in items)

        order = Order.objects.create(user=request.user, total_amount=total_amount)
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
            )
            item.product.stock -= item.quantity
            item.product.save(update_fields=['stock'])

        cart.items.all().delete()

        Payment.objects.create(order=order, gateway='esewa')
        payment_fields = build_payment_form_fields(order=order, amount=total_amount)

        return Response(
            {'order': OrderSerializer(order).data, 'esewa': payment_fields},
            status=status.HTTP_201_CREATED,
        )


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class VendorOrdersView(generics.ListAPIView):
    """Admin: orders that include at least one of their own products."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not (user.is_vendor and user.is_approved):
            return Order.objects.none()
        return Order.objects.filter(items__product__created_by=user).distinct().prefetch_related('items')


class AllOrdersView(generics.ListAPIView):
    """Super admin: all orders, filterable by admin/vendor, date range, and status."""

    serializer_class = OrderSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        qs = Order.objects.all().prefetch_related('items')

        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            qs = qs.filter(items__product__created_by_id=vendor_id).distinct()

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        return qs


class DashboardStatsView(APIView):
    """Super admin: high-level totals + sales breakdown per vendor."""

    permission_classes = [IsSuperAdmin]

    def get(self, request):
        paid_orders = Order.objects.filter(status__in=['paid', 'shipped', 'delivered'])
        total_sales = paid_orders.aggregate(total=Sum('total_amount'))['total'] or 0

        by_vendor = (
            OrderItem.objects.filter(order__status__in=['paid', 'shipped', 'delivered'])
            .values('product__created_by__username', 'product__created_by_id')
            .annotate(
                total_sales=Sum('price_at_purchase'),
                items_sold=Sum('quantity'),
                order_count=Count('order', distinct=True),
            )
            .order_by('-total_sales')
        )

        return Response({
            'total_sales': total_sales,
            'total_orders': Order.objects.count(),
            'total_users': User.objects.filter(role=User.Role.USER).count(),
            'total_admins': User.objects.filter(role=User.Role.ADMIN).count(),
            'sales_by_vendor': list(by_vendor),
        })

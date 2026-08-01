from django.urls import path

from .views import (
    AddToCartView,
    AllOrdersView,
    CartItemDetailView,
    CartView,
    CheckoutView,
    DashboardStatsView,
    MyOrdersView,
    VendorOrdersView,
)

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart-detail'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/items/<int:pk>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    path('orders/checkout/', CheckoutView.as_view(), name='order-checkout'),
    path('orders/mine/', MyOrdersView.as_view(), name='orders-mine'),
    path('orders/vendor/', VendorOrdersView.as_view(), name='orders-vendor'),
    path('orders/all/', AllOrdersView.as_view(), name='orders-all'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]

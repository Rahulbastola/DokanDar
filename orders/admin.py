from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'total_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['order_id', 'user__username']
    inlines = [OrderItemInline]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']


admin.site.register(CartItem)

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/', include('catalog.urls')),
    path('api/', include('orders.urls')),
    path('api/payment/', include('payments.urls')),

    # Vanilla HTML/CSS/JS frontend
    path('', TemplateView.as_view(template_name='products.html'), name='home'),
    path('login.html', TemplateView.as_view(template_name='login.html'), name='login-page'),
    path('register.html', TemplateView.as_view(template_name='register.html'), name='register-page'),
    path('products.html', TemplateView.as_view(template_name='products.html'), name='products-page'),
    path('product.html', TemplateView.as_view(template_name='product.html'), name='product-page'),
    path('cart.html', TemplateView.as_view(template_name='cart.html'), name='cart-page'),
    path('orders.html', TemplateView.as_view(template_name='orders.html'), name='orders-page'),
    path('vendor.html', TemplateView.as_view(template_name='vendor.html'), name='vendor-page'),
    path('admin-dashboard.html', TemplateView.as_view(template_name='admin_dashboard.html'), name='admin-dashboard-page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

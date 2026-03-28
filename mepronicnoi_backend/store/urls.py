from django.urls import path
from . import views

urlpatterns = [
    # ─── หน้าเว็บ ───────────────────────────────────────────────────────────
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:pk>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # ─── Auth ───────────────────────────────────────────────────────────────
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ─── API (JSON) ─────────────────────────────────────────────────────────
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/<int:pk>/', views.api_product_detail, name='api_product_detail'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/cart/', views.api_cart, name='api_cart'),
    path('api/cart/add/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/cart/remove/', views.api_remove_from_cart, name='api_remove_from_cart'),
]

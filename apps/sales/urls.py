from django.urls import path
from . import views

urlpatterns = [
    # POS
    path('', views.pos_dashboard, name='pos_dashboard'),
    path('search/', views.search_products, name='search_products'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Shift management
    path('shift/', views.shift_select, name='shift_select'),
    path('shift/open/<int:register_id>/', views.shift_open, name='shift_open'),
    path('shift/close/', views.shift_close, name='shift_close'),

    # Order actions
    path('void/<int:order_id>/', views.void_sale, name='void_sale'),
]

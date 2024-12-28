from django.urls import path
from .views import *

urlpatterns = [
    path('', ProductListView.as_view(), name='main'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='product'),
    path('category/<slug:slug>/', ProductByCategoryView.as_view(), name='category'),
    path('login/', user_login_view, name='login'),
    path('logout/', user_logout_view, name='logout'),
    path('registration/', register_user_view, name='register'),
    path('add_favorite/<slug:slug>/', save_favorite_product, name='add_favorite'),
    path('my_favorite/', FavoriteListView.as_view(), name='my_favorite'),
    path('sales/', SalesProductListView.as_view(), name='sales'),
    path('add_product/<slug:slug>/<str:action>/', add_product_order, name='add_product'),
    path('my_cart/', my_cart_view, name='my_cart'),
    path('delete/<int:pk>/<int:order>/', delete_products_cart, name='delete'),
    path('checkout/', checkout_view, name='checkout'),
    path('payment/', create_checkout_session, name='payment'),
    path('success/payment/', success_payment, name='success')
]
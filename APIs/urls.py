from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

# app_name = 'APIs'  # Add namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('api/register/', views.register_user, name='register_user'),
    path('api/login/', views.login_user, name='login_user'),
    path('login/', views.login_view, name='login_view'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),

    # path("api/auth/google/", views.google_auth, name="google_auth"),
    
    path('api/logout/', views.logout_user, name='logout_user'),
    path('api/login-sessions/<str:user_id>/', views.get_user_login_sessions, name='login_sessions'),
    path('register_page/', views.register_page, name='register_page'),  # Added trailing slash
    path('acc_details/', views.acc_details, name='acc_details'),  # Added trailing slash
    path('address/', views.address, name='address'),  # Added trailing slash
    # path('bag/', views.bag, name='bag'),  # Added trailing slash
    path('checkout/', views.checkout, name='checkout'),  # Added trailing slash
    path('order-complete/', views.order_complete, name='order_complete'),
    # path('conformation/', views.conformation, name='conformation'),  # Added trailing slash
    path('dashboard/', views.dashboard, name='dashboard'),  # Added trailing slash
    path('item_sort/', views.item_sort, name='item_sort'),  # Added trailing slash
    path('orders/', views.orders, name='orders'),  # Added trailing slash
    # path('product_item/', views.product_item, name='product_item'),  # Added trailing slash
    path('wishlist/', views.wishlist, name='wishlist'),  # Added trailing slash
    path('about-us/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),



    # Product Management URLs
    # path('api/products/add/', views.add_product, name='add_product'),
    path('api/products/all/', views.get_all_products, name='get_all_products'),
    path('api/products/update/<str:product_id>/', views.update_product, name='update_product'),
    path('api/products/delete/<str:product_id>/', views.delete_product, name='delete_product'),
    path('api/products/active/', views.get_active_products, name='get_active_products'),
    path('api/products/unavailable/', views.get_unavailable_products, name='get_unavailable_products'),
    path('api/products/<str:product_id>/', views.get_product_details, name='get_product_details'),

    # path('api/products/add_to_cart/', views.add_to_cart, name="add_to_cart"),
    path('api/orders/place/', views.place_order, name="place_order"),
    path('api/cart/<str:user_id>/', views.get_cart, name="get_cart"),
    path('api/orders/<str:user_id>/', views.get_orders, name="get_orders"),

    # path('products/', views.product_list, name='product_list'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('product/<str:product_id>/add-review/', views.add_review, name='add_review'),

    path('cart/', views.cart, name='cart'),
    path('cart/items/', views.get_cart_items, name='get_cart_items'),
    path('cart/update-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove-item/', views.remove_from_cart, name='remove_from_cart'),

    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),

    path('api/password-reset/', views.password_reset_request, name='password_reset_request'),
    path('api/login/', views.login_user, name='login_user'),
    path('api/register/', views.register_user, name='register_user'),
         
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='USER/password_reset_done.html'
         ),
         name='password_reset_done'),
         
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='USER/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
         
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='USER/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('customer-chat/', views.customer_chat, name='customer_chat'),
    path('customer-details/', views.customer_details, name='customer_details'),
    path('customers-list/', views.customers_list, name='customers_list'),
    path('customer-stats/', views.customer_stats, name='customer_stats'),
    path('login-dashboard/', views.login_dashboard, name='login_dashboard'),
    path('orders-detail/', views.orders_detail, name='orders_detail'),
    path('orders-list/', views.orders_list, name='orders_list'),
    path('add-product/', views.add_product, name='add-product'),
    path('editBanners/', views.editBanners, name='editBanners'),
    path('productsList/', views.productsList, name='productsList'),



    # TEST
    path('test-view/', views.test_view, name='test_view'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


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

    path('account/update/', views.update_account_details, name='update_account_details'),
    # path('account/details/', views.account_details, name='account_details'),



    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('api/google/login/<str:mode>/', views.google_login, name='google_login'),
    path('api/google/callback/', views.google_callback, name='google_callback'),

    # path('user-addresses/', views.user_addresses, name='user_addresses'),-
    path('save-address/', views.save_address, name='save_address'),
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
   path("search-suggestions/", views.search_suggestions, name="search-suggestions"),  # Enhanced
    # Product Management URLs
    # path('api/products/add/', views.add_product, name='add_product'),
    path('api/products/all/', views.get_all_products, name='get_all_products'),
    path('api/products/update/<str:product_id>/', views.update_product, name='update_product'),
    path('api/products/delete/<str:product_id>/', views.delete_product, name='delete_product'),
    path('api/products/active/', views.get_active_products, name='get_active_products'),
    path('api/products/unavailable/', views.get_unavailable_products, name='get_unavailable_products'),
    path('api/products/<str:product_id>/', views.get_product_details, name='get_product_details'),

    # path('api/products/add_to_cart/', views.add_to_cart, name="add_to_cart"),
    # path('api/orders/place/', views.place_order, name="place_order"),
    path('api/cart/<str:user_id>/', views.get_cart, name="get_cart"),
    path('api/orders/<str:user_id>/', views.get_orders, name="get_orders"),

    # path('products/', views.product_list, name='product_list'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('product/<str:product_id>/add-review/', views.add_review, name='add_review'),

    path('cart/', views.cart, name='cart'),
    path('cart/items/', views.get_cart_items, name='get_cart_items'),
    path('cart/update-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),



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
    path('customer-details/<str:user_id>/', views.customer_details, name='customer_details'), # DONE
    path('customers-list/', views.customers_list, name='customers_list'), # DONE
    path('customer-stats/', views.customer_stats, name='customer_stats'),
    path('login-dashboard/', views.login_dashboard, name='login_dashboard'),
    path('order-details/<str:order_no>/', views.order_details, name='order_details'), # DONE
    path('orders-list/', views.orders_list, name='orders_list'), # DONE
    path('add-product/', views.add_product, name='add-product'), # DONE BUT NEED TO MODIFY IT
    path('api/add-product/', views.api_add_product, name='api_add_product'), # IN PROGRESS
    path('editBanners/', views.editBanners, name='editBanners'), # IN PROGRESS
    path("api/upload-product-images/", views.upload_product_images, name="upload-product-images"),
    path('api/categories/', views.search_categories, name='search_categories'),
    path("cart/products/", views.get_cart_products, name="get_cart_products"),
    path("api/top_rated/", views.top_rated_products, name="top_rated"),
    path("api/latest-products/", views.get_latest_products, name="get_latest_products"),# path('productsList/', views.productsList, name='productsList'),

    # COUPONS APIs
    path("generate-coupons/", views.generate_coupons, name="generate_coupons"),
    path("validate-coupon/<str:code>/", views.validate_coupon, name="validate_coupon"),
    path("redeem-coupon/<str:code>/", views.redeem_coupon, name="redeem_coupon"),
    path("delete-expired-coupons/", views.delete_expired_coupons, name="delete_expired_coupons"),


    # TEST
    path('test-view/', views.test_view, name='test_view'),

    # Wishlist APIs
    path('api/wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),  # Add to wishlist
    path('api/wishlist/', views.get_wishlist, name='get_wishlist'),  # Get wishlist
    path('api/wishlist/remove/<str:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),  # Remove from wishlist
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


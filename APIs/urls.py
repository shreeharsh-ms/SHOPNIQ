from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/register/', views.register_user, name='register_user'),
    path('api/login/', views.login_user, name='login_user'),
    path("api/auth/google/", views.google_auth, name="google_auth"),
    
    path('api/logout/', views.logout_user, name='logout_user'),
    path('api/login-sessions/<str:user_id>/', views.get_user_login_sessions, name='login_sessions'),
    path('register_page/', views.register_page, name='register_page'),  # Added trailing slash
    path('acc_details/', views.acc_details, name='acc_details'),  # Added trailing slash
    path('address/', views.address, name='address'),  # Added trailing slash
    path('bag/', views.bag, name='bag'),  # Added trailing slash
    path('checkout/', views.checkout, name='checkout'),  # Added trailing slash
    path('conformation/', views.conformation, name='conformation'),  # Added trailing slash
    path('dashboard/', views.dashboard, name='dashboard'),  # Added trailing slash
    path('item_sort/', views.item_sort, name='item_sort'),  # Added trailing slash
    path('orders/', views.orders, name='orders'),  # Added trailing slash
    # path('product_item/', views.product_item, name='product_item'),  # Added trailing slash
    path('wishlist/', views.wishlist, name='wishlist'),  # Added trailing slash
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),


    # Product Management URLs
    path('api/products/add/', views.add_product, name='add_product'),
    path('api/products/all/', views.get_all_products, name='get_all_products'),
    path('api/products/update/<str:product_id>/', views.update_product, name='update_product'),
    path('api/products/delete/<str:product_id>/', views.delete_product, name='delete_product'),
    path('api/products/active/', views.get_active_products, name='get_active_products'),
    path('api/products/unavailable/', views.get_unavailable_products, name='get_unavailable_products'),
    path('api/products/<str:product_id>/', views.get_product_details, name='get_product_details'),

    path('api/products/add_to_cart/', views.add_to_cart, name="add_to_cart"),
    path('api/orders/place/', views.place_order, name="place_order"),
    path('api/cart/<str:user_id>/', views.get_cart, name="get_cart"),
    path('api/orders/<str:user_id>/', views.get_orders, name="get_orders"),
    # path('products/', views.product_list, name='product_list'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('product/<str:product_id>/add-review/', views.add_review, name='add_review'),


]


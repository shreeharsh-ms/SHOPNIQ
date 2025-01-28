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
    path('product_item/', views.product_item, name='product_item'),  # Added trailing slash
    path('wishlist/', views.wishlist, name='wishlist'),  # Added trailing slash
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),
]


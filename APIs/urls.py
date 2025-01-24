from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register_page', views.register_page, name='register_page'),
    path('acc_details', views.acc_details, name='acc_details'),
    path('address', views.address, name='address'),
    path('bag', views.bag, name='bag'),
    path('checkout', views.checkout, name='checkout'),
    path('conformation', views.conformation, name='conformation'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('item_sort', views.item_sort, name='item_sort'),
    path('orders', views.orders, name='orders'),
    path('product_item', views.product_item, name='product_item'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),
]

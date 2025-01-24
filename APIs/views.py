from django.shortcuts import render

def index(request):
    return render(request, 'Home/index.html')

def register_page(request):
    return render(request, 'REGISTER/register.html')

def acc_details(request):
    return render(request, 'USER/Acc_details.html')

def address(request):
    return render(request, 'USER/Address.html')

def bag(request):
    return render(request, 'USER/Bag.html')

def checkout(request):
    return render(request, 'USER/CheckOut.html')

def conformation(request):
    return render(request, 'USER/Conformation.html')

def dashboard(request):
    return render(request, 'USER/Dashboard.html')

def item_sort(request):
    return render(request, 'USER/Item-Sort.html')

def orders(request):
    return render(request, 'USER/Orders.html')

def product_item(request):
    return render(request, 'USER/product-Item.html')

def wishlist(request):
    return render(request, 'USER/WishList.html')

def about_us(request):
    return render(request, 'Home/ABOUTUS.html')

def contact_us(request):
    return render(request, 'Home/ContactUS.html')
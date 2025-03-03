from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from APIs.mongodb import MongoDBUser, MongoDBReview,MongoDBDescription,MongoDBCategory,MongoDBProduct,MongoDBBrand ,MongoDBCart, MongoDBOrders  # Import MongoDB Helper
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from datetime import datetime, timezone
import pymongo
import pytz
from bson.objectid import ObjectId
from django.conf import settings
from django.http import Http404
from APIs.mongodb import contact_messages
from django.contrib.auth.decorators import login_required  # Add this import
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
import jwt
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.middleware.csrf import get_token
from django.http import JsonResponse
from .permissions import IsMongoAuthenticated
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pymongo import MongoClient
from SHOPNIQ.settings import MONGO_DB
# client = MongoClient("mongodb://localhost:27017/")
# db = client["test"]  # Specify the 'test' database
# products_collection = db["products"]
# descriptions_collection = db["descriptions"] 
products_collection = MONGO_DB["products"]
descriptions_collection = MONGO_DB["descriptions"]
import os
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# from .mongodb import cart_collection, products_collection  # Ensure these are defined


# Y2qK9yW21YLMQCUT
# daredevilgamerdream

ist = pytz.timezone('Asia/Kolkata')

# MongoDB setup
# client = pymongo.MongoClient(
#     settings.MO,
#     connectTimeoutMS=30000,  # Increase the connection timeout
#     socketTimeoutMS=30000    # Increase the socket timeout
# )

db = settings.MONGO_DB
products_collection = settings.MONGO_DB['products']
# products_collection = db["products"]
products_collection = db["products"]

cart_collection_collection = settings.MONGO_DB['cart']


login_sessions = settings.MONGO_DB["login_sessions"]

try:
    # Test MongoDB connection
    products_collection = settings.MONGO_DB["products"]
    
    # Try to fetch one product
    test_product = products_collection.find_one()
    print("Test MongoDB Connection:", test_product)
except Exception as e:
    print("MongoDB Connection Error:", str(e))

def login_view(request):
    return render(request, 'REGISTER/register.html')

from django.shortcuts import redirect
import urllib.parse
from django.conf import settings

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/api/google/callback/"

def google_login(request, mode):
    """ Redirect user to Google OAuth for Sign-In or Sign-Up """
    
    if mode not in ["signin", "signup"]:
        return JsonResponse({"error": "Invalid mode"}, status=400)

    google_oauth_url = "https://accounts.google.com/o/oauth2/auth"
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,  # No query parameters!
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": mode,  # Use state instead of query param
    }

    return redirect(f"{google_oauth_url}?{urllib.parse.urlencode(params)}")


from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from .mongodb import MongoDBUser
from .auth import MongoUser
import requests

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
REDIRECT_URI = "http://127.0.0.1:8000/api/google/callback/"

def google_callback(request):
    """Handles Google OAuth Sign-In & Sign-Up"""
    code = request.GET.get("code")
    mode = request.GET.get("state")  # Read mode from state parameter

    if not code or mode not in ["signin", "signup"]:
        return JsonResponse({"error": "Authorization failed"}, status=400)

    # Step 1: Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()

    if "access_token" not in token_json:
        return JsonResponse({"error": "Failed to authenticate with Google"}, status=400)

    access_token = token_json["access_token"]

    # Step 2: Fetch user info
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    user_info_response = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_info_response.json()

    google_email = user_info.get("email")
    google_name = user_info.get("name")

    if not google_email:
        return JsonResponse({"error": "Unable to get email from Google"}, status=400)

    # Step 3: Handle Sign-In and Sign-Up
    user_data = MongoDBUser.get_user_by_email(google_email)

    if mode == "signin":
        if not user_data:
            return JsonResponse({"error": "User does not exist. Please sign up first."}, status=403)

        user = MongoUser(user_data)
        request.session["user_id"] = str(user.id)
        request.session["role"] = user.role
        return redirect("/")

    elif mode == "signup":
        if user_data:
            return JsonResponse({"error": "User already exists. Please sign in instead."}, status=403)

        new_user = MongoDBUser.create_user(email=google_email, password=None, username=google_name, role="customer")

        user = MongoUser(new_user)
        request.session["user_id"] = str(user.id)
        request.session["role"] = user.role
        return redirect("/")

    return JsonResponse({"error": "Invalid mode"}, status=400)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.middleware.csrf import get_token
from .permissions import IsAdmin, IsManager
from .mongodb import MongoDBUser
import bcrypt

@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can register
def register_user(request):
    data = request.data

    # Extract the fields from the request data
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    phone_number = data.get("phone_number", None)  # Optional field
    role = data.get("role", "user")  # Default role = user
    address = data.get("address", [])  # Default empty list for address
    orders = data.get("orders", [])  # Default empty list for orders

    # Check if the user already exists
    if MongoDBUser.get_user_by_email(email):
        return Response({"error": "User already exists"}, status=400)

    # Create the user
    user_id = MongoDBUser.create_user(
        username=username,
        email=email,
        password=password,
        role=role,
        phone_number=phone_number
    )

    return Response({
        "success": True,
        "message": "Registration successful!"
    }, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(request, email=email, password=password)

    if user is not None:
        request.session['user_id'] = user.id  # ✅ Store user ID in session
        request.session['role'] = user.role   # ✅ Store user role in session
        return JsonResponse({
            "success": True,
            "message": "Login successful",
            "role": user.role
        }, status=200)

    return JsonResponse({
        "success": False,
        "message": "Invalid email or password"
    }, status=401)


from django.contrib.auth import logout as auth_logout
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsMongoAuthenticated  # Assuming this is your custom permission

from django.contrib.auth import logout as auth_logout

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    print("@@@@@@@@@@@User is logged out@@@@@@@@@@@@@")
    auth_logout(request)  # Clears session on the server side
    request.session.flush()  # Clears the session data on the server
    response = Response({"success": True, "message": "Logout successful"}, status=200)
    

    return response

@api_view(['GET'])
@permission_classes([IsAdmin])  # Only admins can access this
def admin_dashboard(request):
    return Response({"message": "Welcome, Admin!"})

@api_view(['GET'])
@permission_classes([IsManager])  # Only managers can access this
def manager_dashboard(request):
    return Response({"message": "Welcome, Manager!"})

from social_django.utils import psa
from django.contrib.auth import login
from datetime import datetime
import pytz
from django.http import JsonResponse
import requests
from SHOPNIQ import settings

ist = pytz.timezone('Asia/Kolkata')

users_collection = settings.MONGO_DB["users"]
@api_view(['POST'])
@psa('social:complete')
def google_auth(request):
    import json
    body = json.loads(request.body.decode('utf-8'))
    access_token = body.get("access_token")

    if not access_token:
        return JsonResponse({"error": "Missing access token"}, status=400)

    google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={access_token}"
    response = requests.get(google_url)
    
    if response.status_code != 200:
        return JsonResponse({"error": "Invalid token"}, status=400)
    
    user_info = response.json()
    email = user_info["email"]
    username = user_info["name"]

    session_data = {
        "email": email,
        "username": username,
        "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "logout_time": None
    }

    session_id = login_sessions.insert_one(session_data).inserted_id
    return JsonResponse({"session_id": str(session_id), "user": session_data})

@api_view(['GET'])
def get_user_login_sessions(request, user_id):
    """Fetch all login sessions for a specific user."""
    sessions = list(login_sessions.find({"user_id": user_id}, {"_id": 0}))
    print(sessions)
    return Response({"login_sessions": sessions}, status=200)

# API to register a new user in MongoDB

def register_page(request):
    return render(request, 'REGISTER/register.html')


def index(request):
    user_id = request.session.get('user_id')
    print(f'######################{user_id}')
    print("Index view called!")
    
    try:
        print("\n🔹 Debugging Authentication 🔹")
        print("Is user authenticated?", request.user.is_authenticated)
        print("User:", request.user)
        print("User ID from request:", getattr(request.user, "id", "No ID"))
        print("Session Data:", request.session.items())
        
        if request.user.is_authenticated:
            print("Welcome, authenticated user! user:", str(request.user))
            # return JsonResponse({"message": "Welcome, authenticated user!", "user": str(request.user)}, status=200)
        else:
            # return JsonResponse({"error": "User is not aut
            # henticated"}, status=401)
            print("user not found")
        # Fetch all active products and sort by date
        print("Attempting to fetch products...")
        products = list(products_collection.find())

        current_user = request.user

        # Process each product
        processed_products = []
        for product in products:
            processed_product = {
                "id": str(product["_id"]),
                "name": product.get("name", ""),
                "category_id": str(product.get("category_id", "")),  # Use ObjectId for category
                "subcategory": product.get("subcategory", ""),
                "price": product.get("price", 0),
                "stock": int(product.get("stock", 0)),
                "variants": product.get("variants", {}),  # Dictionary for variants (e.g., color, size)
                "tags": product.get("tags", []),
                "description_id": str(product.get("description_id", "")),  # ObjectId for description
                "reviews": [str(review) for review in product.get("reviewsDictionary", [])],  # Convert ObjectIds to strings
                "weight": product.get("weight", ""),
                "dimensions": product.get("dimensions", {}),
                "images": product.get("images", []),  # List of image dictionaries
                "banner_img": product.get("banner_img", {}),  # Banner image details
                "status": product.get("status", "active"),
                "created_at": product.get("created_at", ""),
                "updated_at": product.get("updated_at", "")
            }
            processed_products.append(processed_product)


        # Get cart data for the current user
        cart_items = []
        cart_total = 0
        
        if request.user.is_authenticated:
            print("User is authenticated:", request.user)
            try:
                # Use MongoDB user ID from session instead of Django user ID
                mongo_user_id = request.session.get('user_id')
                print("Looking for cart with MongoDB user_id:", mongo_user_id)
                
                if mongo_user_id:
                    cart = cart_collection.find_one({"user_id": ObjectId(mongo_user_id)})
                    print("Found cart:", cart)
                    
                    if cart:
                        for item in cart.get("products", []):
                            try:
                                product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
                                print(f"Processing product: {item['product_id']}")
                                print(f"Found product: {product}")
                                
                                if product:
                                    quantity = item["quantity"]
                                    # price = float(product["discounted_price"])
                                    # cart_total += item_total
                                    # print(cart_total)
                                    price = float(product.get("discounted_price") or product.get("price", 0))
                                    item_total = price * quantity
                                    cart_total += item_total
                                    
                                    cart_items.append({
                                        "id": item["product_id"],
                                        "product": {
                                            "id": str(product["_id"]),
                                            "name": product["name"],
                                            "image": {
                                                "url": product["image_url"]
                                            },
                                            "price": price
                                        },
                                        "quantity": quantity,
                                        "color": item.get("color"),
                                        "size": item.get("size"),
                                        "get_total_price": "{:.2f}".format(item_total)
                                    })
                            except Exception as product_error:
                                print(f"Error processing product: {str(product_error)}")
                                continue
                else:
                    print("No MongoDB user ID found in session")
            except Exception as cart_error:
                print(f"Error fetching cart data: {str(cart_error)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
        else:
            print("User is not authenticated")

        # Combine all context data
        print(f'44444444444444444444444444444444444444444444444444 {processed_products}');
        context = {
            'user': current_user,
            "products": processed_products,
            "categories": list(products_collection.distinct("category")),
            "cart_items": cart_items,
            "cart_total": "{:.2f}".format(cart_total),
            "cart_items_count": len(cart_items)
        }

        return render(request, "Home/index.html", context)
    

    except Exception as e:
        print(f"Error in index view: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return render(request, "Home/index.html", {
            "message": "Unable to fetch products",
            "cart_items": [],
            "cart_total": "0.00",
            "cart_items_count": 0
        })


def get_cart_products(request):
    """Fetch the cart along with product details using session-based user ID."""
    user_id = request.session.get('user_id')  # Fetch user ID from session

    if not user_id:
        return JsonResponse({"cart": [], "total_amount": 0, "message": "User not logged in"}, status=401)

    # Get the cart for the user
    cart = MongoDBCart.get_user_cart(user_id)
    if not cart or not cart.get("products"):
        return JsonResponse({"cart": [], "total_amount": 0, "message": "Cart is empty"}, status=200)

    # Extract product IDs and quantities from the cart
    product_quantities = {item["product_id"]: item["quantity"] for item in cart["products"]}
    product_ids = [ObjectId(pid) for pid in product_quantities.keys()]

    # Fetch product details from MongoDB
    products_collection = db["products"]
    products = products_collection.find({"_id": {"$in": product_ids}})

    # Map products with their quantity and calculate total amount
    products_data = []
    total_amount = 0

    for product in products:
        product_id_str = str(product["_id"])
        quantity = product_quantities.get(product_id_str, 1)  # Default to 1 if missing

        product_price = product.get("price", 0)
        item_total = product_price * quantity
        total_amount += item_total

        products_data.append({
            "_id": product_id_str,
            "name": product.get("name", "Unknown"),
            "price": product_price,
            "image": product["images"][0] if product.get("images") else product.get("banner_img", ""),  # Fetch first image
            "quantity": quantity
        })

    return JsonResponse({
        "cart": products_data,
        "total_amount": round(total_amount, 2),  # Ensure proper rounding for currency
        "created_at": cart["created_at"].isoformat() if cart.get("created_at") else None,
        "updated_at": cart["updated_at"].isoformat() if cart.get("updated_at") else None
    }, safe=False)

def acc_details(request):
    return render(request, 'USER/Acc_details.html')

def address(request):
    return render(request, 'USER/Address.html')

from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib import messages


def checkout(request):
    if request.method == 'POST':
        # Fetch user ID from session
        user_id = request.session.get('user_id')
        if not user_id:
            return render(request, 'USER/CheckOut.html', {"error": "User not logged in."})

        # Fetch cart items
        cart = cart_collection.find_one({"user_id": ObjectId(user_id)})
        cart_items = cart.get('products', []) if cart else []
        print("@@@@@@@@@",cart_items)
        
        
                    

        if not cart_items:
            return render(request, 'USER/CheckOut.html', {"error": "Your cart is empty."})

        # Extract checkout details
        shipping_address = {
            "FirstName": request.POST.get('checkout_first_name', '').strip(),
            "LastName": request.POST.get('checkout_last_name', '').strip(),
            "CompanyName": request.POST.get('checkout_company_name', '').strip(),
            "CountryRegion": request.POST.get('search-keyword', '').strip(),
            "StreetAddress": request.POST.get('checkout_street_address', '').strip(),
            "StreetAddress2": request.POST.get('checkout_street_address_2', '').strip(),
            "City": request.POST.get('checkout_city', '').strip(),
            "Zipcode": request.POST.get('checkout_zipcode', '').strip(),
            "Phone": request.POST.get('checkout_phone', '').strip(),
            "Email": request.POST.get('checkout_email', '').strip(),
            "OrderNotes": request.POST.get('order_notes', '').strip()
        }

        # Calculate order total
        total_amount = 0  # Initialize total amount
        items = []  # List to store formatted items

        for item in cart_items:
            product = products_collection.find_one({"_id": ObjectId(item['product_id'])})
            if product:  # Check if the product exists
                price = product.get('price', 0)  # Get price, default to 0 if not found
                quantity = item.get('quantity', 1)  # Default to 1 if not found
                subtotal = price * quantity  # Calculate subtotal

                # Append item in the correct format for place_order
                items.append({
                    "product_id": str(item["product_id"]),
                    "product_name": product.get("name", "Unknown Product"),  # Use DB name
                    "quantity": quantity,
                    "price_per_unit": price,
                    "subtotal": subtotal
                })

                total_amount += subtotal  # Update total amount

        print("Total amt: ", total_amount)  # Print the total amount

        # Generate unique transaction ID
        transaction_id = f"TXN{ObjectId()}"



        # Place order
        order_id = MongoDBOrders.place_order(
            user_id=user_id,
            items=items,
            total_amount=total_amount,
            shipping_address=shipping_address,
            payment_status="Pending",
            transaction_id=transaction_id,
            estimated_delivery_days=5
        )

        # Clear cart after order
        cart_collection.update_one({"user_id": ObjectId(user_id)}, {"$set": {"products": []}})

        # Redirect to order confirmation
        return redirect('order_complete')

    # Render checkout page
    user_id = request.session.get('user_id')
    context = {}

    if user_id:
            # Fetch user data if needed
            user_data = MongoDBUser.get_user_by_id(user_id)  # Replace with your actual method to get user data
            context['user'] = user_data

            # Fetch cart items for the user
            cart = cart_collection.find_one({"user_id": user_id})  # Fetch the user's cart
            if cart:
                context['cart_items'] = cart.get('products', [])
                # Calculate total with error handling
                cart_total = 0
                for item in context['cart_items']:
                    try:
                        # Fetch product details from the database
                        product = products_collection.find_one({"_id": ObjectId(item['product_id'])})
                        if product:
                            price = product.get('price', 0)  # Default to 0 if price is not found
                            quantity = item['quantity']  # Access the quantity
                            cart_total += price * quantity  # Calculate total
                        else:
                            print(f"Product not found for ID: {item['product_id']}")
                    except Exception as e:
                        print(f"Error fetching product details: {e}")

                context['cart_total'] = cart_total  # Set the total in context

            return render(request, 'USER/CheckOut.html', context)
@login_required
def order_complete(request):
    # Verify order exists and is complete
    if 'order_id' not in request.session:
        messages.warning(request, 'No order to display')
        return redirect('cart')
        
    # Your order complete view code
    return render(request, 'USER/order_complete.html')

def dashboard(request):
    return render(request, 'USER/Dashboard.html')

import logging

logger = logging.getLogger(__name__)


@login_required
def item_sort(request):
    try:
        # 🔹 Step 1: Get Query Parameters
        query = request.GET.get('query', '').strip()
        category_query = request.GET.get('category', '').strip()
        sort_by = request.GET.get('sort_by', 'price')
        order = request.GET.get('order', 'desc')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        brand_query = request.GET.get('brand', '').strip()

        product_query = {}

        # 🔹 Step 2: Text Search (Name, Tags, Description)
        search_conditions = []
        brand_categories = None
        is_product_name_search = False

        if query:
            search_conditions.extend([
                {"name": {"$regex": query, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": query, "$options": "i"}}}
            ])

            # Search in descriptions
            matching_descriptions = descriptions_collection.find(
                {"description": {"$regex": query, "$options": "i"}}
            )
            description_ids = [desc["PID"] for desc in matching_descriptions]
            if description_ids:
                search_conditions.append({"_id": {"$in": description_ids}})

            # Get brand categories if the query is based on a product name
            product = products_collection.find_one({"name": {"$regex": f"^{query}$", "$options": "i"}})
            if product and "brand_id" in product:
                brand_categories = MongoDBBrand.get_brand_categories(product["brand_id"])
                is_product_name_search = True  # ✅ Mark as product name search

        if search_conditions:
            product_query["$or"] = search_conditions

        # 🔹 Step 3: Always Fetch Top 10 Categories
        top_categories = MongoDBCategory.get_all_categories()
        top_categories = sorted(top_categories, key=lambda x: x["product_count"], reverse=True)[:10]

        category_brands = {}
        selected_category_brands = None

        # 🔹 Step 4: Filter by Category and Fetch Brands Accordingly
        if category_query:
            category_ids = MongoDBCategory.get_category_ids_by_name(category_query)
            if not category_ids and ObjectId.is_valid(category_query):
                category_ids = [category_query]

            if category_ids:
                product_query["category_id"] = {"$in": [ObjectId(cat_id) for cat_id in category_ids]}
                selected_category_brands = MongoDBBrand.get_brands_by_category(category_ids[0])  # Fetch brands under the category
        else:
            category_brands = MongoDBBrand.get_product_brands()  # Fetch all brands if no category is searched

        # 🔹 Step 5: Filter by Brand
        if brand_query:
            brand_id = MongoDBBrand.get_brand_id_by_name(brand_query)
            if brand_id:
                product_query["brand_id"] = ObjectId(brand_id)

        # 🔹 Step 6: Apply Price Filtering
        price_filter = {}
        if min_price and min_price.isdigit():
            price_filter["$gte"] = float(min_price)
        if max_price and max_price.isdigit():
            price_filter["$lte"] = float(max_price)
        if price_filter:
            product_query["price"] = price_filter

        # 🔹 Step 7: Sorting
        sort_order = -1 if order == 'desc' else 1
        sort_field_map = {
            "price": "price",
            "name": "name",
            "description": "description_id",
            "tags": "tags",
            "category": "category_id",
            "brand": "brand_id",
            "product_count": "product_count"
        }
        sort_field = sort_field_map.get(sort_by, "price")

        # 🔹 Step 8: Fetch & Sort Products
        products = products_collection.find(product_query).sort(sort_field, sort_order)

        # 🔹 Step 9: Convert to JSON-safe List
        products_list = []
        for product in products:
            try:
                serialized_product = {
                    'id': str(product['_id']),
                    'name': product.get('name', 'Unnamed Product'),
                    'price': product.get('price', 0),
                    'image': product.get('images', [''])[0] if product.get('images') else '',
                    'description': MongoDBDescription.get_description_by_product_id(product['_id']).get("description", "No description available")
                    if product.get("description_id") else "No description available",
                    'tags': product.get('tags', []),
                    'category': MongoDBCategory.get_category_by_id(product.get('category_id', '')).get("CategoryName", "Uncategorized")
                    if product.get('category_id') else "Uncategorized",
                    'brand': MongoDBBrand.get_brand_by_id(product.get('brand_id', '')).get("name", "No Brand")
                    if product.get('brand_id') else "No Brand",
                    'in_stock': product.get('stock', 0) > 0
                }
                products_list.append(serialized_product)
            except Exception as e:
                print(f"⚠️ Error processing product {product['_id']}: {e}")

        # 🔹 Step 10: Debugging Info
        print(f"🔍 Query: {query}, Category: {category_query}, Brand: {brand_query}, Sort By: {sort_by}, Order: {order}, Min Price: {min_price}, Max Price: {max_price}")
        print(f"🛒 Filtered Products Count: {len(products_list)}")
        print(f"📌 Top Categories: {top_categories}")
        print(f"🔹 Brand Categories: {brand_categories if brand_categories else 'N/A'}")
        print(f"🗂 Selected Category Brands: {selected_category_brands if selected_category_brands else 'N/A'}")
        print(f"📦 All Product Brands: {category_brands}")

        # 🔹 Step 11: Pass Data to Template
        print(f'fuck OFFFF {selected_category_brands if selected_category_brands else category_brands}')
        return render(request, 'USER/Item-Sort.html', {
            'products': products_list,
            'query': query,
            'category': category_query,
            'brand': brand_query,
            'sort_by': sort_by,
            'order': order,
            'min_price': min_price,
            'max_price': max_price,
            'top_categories': top_categories,  
            'brand_categories': brand_categories if brand_categories else None,
            'category_brands': [{'name': brand, 'product_count': 0} for brand in selected_category_brands] 
                if selected_category_brands else []
        })


    except Exception as e:
        print(f"🚨 Error in item_sort: {str(e)}")
        return render(request, 'USER/Item-Sort.html', {
            'products_json': '[]',
            'error_message': 'Unable to fetch products'
        })



@csrf_exempt
def search_suggestions(request):
    """Returns product name, categories, brands, and tags as suggestions."""
    query = request.GET.get("search-keyword", "").strip()

    if not query:
        return JsonResponse({"suggestions": {"products": [], "categories": [], "brands": [], "tags": []}})

    search_conditions = [
        {"name": {"$regex": query, "$options": "i"}},  # Product names
        {"tags": {"$elemMatch": {"$regex": query, "$options": "i"}}}  # Tags
    ]

    # 🔹 Fetch Matching Products
    products = MongoDBProduct.search_products(query, "name", "asc")
    product_suggestions = [product["name"] for product in products]

    # 🔹 Fetch Matching Categories
    categories = MongoDBCategory.get_all_categories()
    category_suggestions = [
        cat["CategoryName"] for cat in categories if query.lower() in cat["CategoryName"].lower()
    ]

    # 🔹 Fetch Matching Brands
    brands = MongoDBBrand.get_all_brands()
    brand_suggestions = [
        brand["name"] for brand in brands if query.lower() in brand["name"].lower()
    ]

    # 🔹 Fetch Matching Tags
    tags = set()
    for product in products:
        for tag in product.get("tags", []):
            if query.lower() in tag.lower():
                tags.add(tag)

    return JsonResponse({
        "suggestions": {
            "products": product_suggestions[:5],  # Limit results to 5 per category
            "categories": category_suggestions[:5],
            "brands": brand_suggestions[:5],
            "tags": list(tags)[:5]
        }
    })


def orders(request):
    return render(request, 'USER/Orders.html')

# def product_item(request):
#     return render(request, 'USER/product-Item.html')


def wishlist(request):
    return render(request, 'USER/WishList.html')

def about_us(request):
    return render(request, 'Home/ABOUTUS.html')

def contact_submit(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            message = request.POST.get('message')
            
            # Create contact entry
            contact_data = {
                "name": name,
                "email": email,
                "message": message,
                "status": "unread",  # For admin to track read/unread messages
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Insert into MongoDB
            result = settings.MONGO_DB.contact_messages.insert_one(contact_data)
            
            if result.inserted_id:
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
            else:
                messages.error(request, 'Sorry, there was an error submitting your message. Please try again.')
                
        except Exception as e:
            print(f"Error in contact submission: {str(e)}")
            messages.error(request, 'An error occurred. Please try again later.')
            
    return redirect('contact_us')

def contact_us(request):
    return render(request, 'Home/ContactUS.html')


from datetime import datetime
from bson import ObjectId
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# MongoDB products collection
products_collection = settings.MONGO_DB["products"]

# API to add a new product to MongoDB
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from bson.objectid import ObjectId
import datetime


@csrf_exempt
def upload_product_images(request):
    print("CHADDDDDDDDDDDDDDDDDDI UPLOADED")
    if request.method == "POST" and request.FILES:
        uploaded_files = request.FILES.getlist("images")  # Multiple images
        image_paths = []

        for file in uploaded_files:
            ext = os.path.splitext(file.name)[-1]
            unique_filename = f"products/{uuid.uuid4().hex}{ext}"
            file_path = default_storage.save(unique_filename, ContentFile(file.read()))

            image_paths.append(f"/media/{file_path}")  # Return media path

        return JsonResponse({"image_paths": image_paths}, status=201)

    return JsonResponse({"error": "Invalid request"}, status=400)

def add_product(request):
    return render(request, 'Admin/add-product.html')


@api_view(['GET'])
def search_categories(request):
    """API endpoint to search categories by name."""
    try:
        search_query = request.GET.get('q', '').strip().lower()  # Get search query from request
        
        # Fetch all categories
        categories = MongoDBCategory.get_all_categories()
        
        # Filter categories based on search query
        if search_query:
            filtered_categories = [
                category for category in categories
                if search_query in category["CategoryName"].lower()
            ]
        else:
            filtered_categories = categories  # Return all if no search query
        
        return JsonResponse({"categories": filtered_categories}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

@api_view(['POST'])
@csrf_exempt
def api_add_product(request):
    """API endpoint to add a new product using MongoDBProduct class."""
    if request.method == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))

            # Extract fields from request body
            name = body.get("name")
            brand_name = body.get("brand_name")  # ✅ Added Brand Name
            category_name = body.get("category_name")
            subcategory = body.get("subcategory")
            actual_price = body.get("actual_price")
            price = body.get("price")
            stock = body.get("stock")
            variants = body.get("variants", {})  # Default to empty dict
            tags = body.get("tags", [])  # Default to empty list
            weight = body.get("weight", "")
            dimensions = body.get("dimensions", {})  # Default to empty dict
            images = body.get("images", [])  # Default to empty list
            description_id = body.get("description_id")
            reviews = body.get("reviews", [])  # Default to empty list
            banner_img = body.get("banner_img", {})

            # Validate required fields
            if not name or not category_name or not actual_price or not price:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Call MongoDBProduct method to insert the product
            product_id = MongoDBProduct.add_product(
                name=name,
                brand_name=brand_name,  # ✅ Added Brand Name to MongoDB insert
                category_name=category_name,
                subcategory=subcategory,
                actual_price=actual_price,
                price=price,
                stock=stock,
                variants=variants,
                tags=tags,
                weight=weight,
                dimensions=dimensions,
                images=images,
                description_id=description_id,
                reviews=reviews,
                banner_img=banner_img
            )

            return JsonResponse({"message": "Product added successfully", "product_id": product_id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@api_view(['GET'])
def get_product_details(request, product_id):
    try:
        # Fetch the product from MongoDB using the product_id
        product = products_collection.find_one({"_id": ObjectId(product_id)})

        if not product:
            return JsonResponse({"error": "Product not found"}, status=404)

        # Fetch category details using category_id from the categories collection
        category = categories_collection.find_one({"_id": ObjectId(product["category_id"])})
        category_name = category["name"] if category else "Unknown Category"

        # Extract product details
        product_data = {
            "id": str(product["_id"]),  # Convert ObjectId to string for the response
            "name": product["name"],
            "description": product.get("description", ""),
            "price": product.get("price", 0.0),
            "stock": product.get("stock", 0),
            "category_id": product["category_id"],  # Keep the category_id
            "subcategory": product.get("subcategory", ""),
            "variants": product.get("variants", {}),
            "tags": product.get("tags", []),
            "weight": product.get("weight", ""),
            "dimensions": product.get("dimensions", {}),
            "images": product.get("images", []),
            "banner_img": product.get("banner_img", {}),
            "reviews": product.get("reviews", []),
            "status": product.get("status", ""),
            "created_at": product.get("created_at", ""),
            "updated_at": product.get("updated_at", ""),
        }

        return JsonResponse({"product": product_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



# API to update a product in MongoDB
@api_view(['PUT'])
@csrf_exempt
def update_product(request, product_id):
    if request.method == "PUT":
        try:
            body = json.loads(request.body.decode('utf-8'))
            updated_data = {}

            # Optionally update fields
            if "name" in body:
                updated_data["name"] = body["name"]
            if "description" in body:
                updated_data["description"] = body["description"]
            if "original_price" in body:
                updated_data["original_price"] = body["original_price"]
            if "discounted_price" in body:
                updated_data["discounted_price"] = body["discounted_price"]
            if "discount" in body:
                updated_data["discount"] = body["discount"]
            if "image_url" in body:
                updated_data["image_url"] = body["image_url"]
            if "stock" in body:
                updated_data["stock"] = body["stock"]
            if "category" in body:
                updated_data["category"] = body["category"]


            updated_data["updated_at"] = datetime.now()

            # Update product in the database
            result = products_collection.update_one(
                {"_id": ObjectId(product_id)}, {"$set": updated_data}
            )

            if result.matched_count == 0:
                return JsonResponse({"error": "Product not found"}, status=404)

            return JsonResponse({"message": "Product updated successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# API to delete a product from MongoDB
@api_view(['DELETE'])
@csrf_exempt
def delete_product(request, product_id):
    if request.method == "DELETE":
        try:
            result = products_collection.delete_one({"_id": ObjectId(product_id)})

            if result.deleted_count == 0:
                return JsonResponse({"error": "Product not found"}, status=404)

            return JsonResponse({"message": "Product deleted successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# API to fetch all products from MongoDB
@api_view(['GET'])
def get_all_products(request):
    try:
        # Retrieve all products from the database
        products = products_collection.find()
        
        # Prepare product data to return
        product_list = []
        for product in products:
            product_data = {
                "name": product["name"],
                "description": product.get("description"),
                "original_price": product["original_price"],
                "discounted_price": product["discounted_price"],
                "discount": product["discount"],
                "image_url": product["image_url"],
                "stock": product["stock"],
                "created_at": product["created_at"],
                "updated_at": product["updated_at"],
            }
            product_list.append(product_data)

        return JsonResponse({"products": product_list})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# API to fetch active products (products with stock > 0)
@api_view(['GET'])
def get_active_products(request):
    try:
        # Retrieve active products (stock > 0)
        active_products = products_collection.find({"stock": {"$gt": 0}})

        # Prepare active product data to return
        active_product_list = []
        for product in active_products:
            product_data = {
                "name": product["name"],
                "description": product.get("description"),
                "original_price": product["original_price"],
                "discounted_price": product["discounted_price"],
                "discount": product["discount"],
                "image_url": product["image_url"],
                "stock": product["stock"],
                "created_at": product["created_at"],
                "updated_at": product["updated_at"],
            }
            active_product_list.append(product_data)

        return JsonResponse({"active_products": active_product_list})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# API to fetch unavailable products (products with stock <= 0)
@api_view(['GET'])
def get_unavailable_products(request):
    try:
        # Retrieve unavailable products (stock <= 0)
        unavailable_products = products_collection.find({"stock": {"$lte": 0}})

        # Prepare unavailable product data to return
        unavailable_product_list = []
        for product in unavailable_products:
            product_data = {
                "name": product["name"],
                "description": product.get("description"),
                "original_price": product["original_price"],
                "discounted_price": product["discounted_price"],
                "discount": product["discount"],
                "image_url": product["image_url"],
                "stock": product["stock"],
                "created_at": product["created_at"],
                "updated_at": product["updated_at"],
            }
            unavailable_product_list.append(product_data)

        return JsonResponse({"unavailable_products": unavailable_product_list})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

#########################################################################################################################################
def get_product_by_id(product_id):
    products_collection = settings.MONGO_DB["products"]
    product = products_collection.find_one({"_id": ObjectId(product_id)})

    if product:
        return {
            "name": product["name"],
            "description": product["description"],
            "original_price": product["original_price"],
            "discounted_price": product["discounted_price"],
            "discount": product["discount"],
            "image_url": product["image_url"],
        }
    return None

from django.http import JsonResponse
from rest_framework.decorators import api_view
import datetime
from django.conf import settings
import json
from bson import ObjectId
from .permissions import IsMongoAuthenticated 

# MongoDB collections
cart_collection = settings.MONGO_DB["cart"]

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes

import traceback  # Add this at the top

@api_view(['POST'])
@permission_classes([IsMongoAuthenticated])
def add_to_cart(request):
    print(f"🚀 Before Auth Check: request.user = {request.user}")

    if not request.user.is_authenticated:
        print("❌ Authentication Failed: User is Anonymous")
        return JsonResponse({"redirect": "/login"}, status=401)

    print("✅ User Authenticated, Proceeding to add to cart")

    try:
        data = request.data
        print(f"Received Data: {data}")  # Log incoming request data

        product_id = data.get('product_id')

        if not product_id or not ObjectId.is_valid(product_id):
            print("❌ Invalid Product ID")
            return JsonResponse({"error": "Invalid Product ID"}, status=400)

        product_id = ObjectId(product_id)

        try:
            quantity = int(data.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1

        print(f"🛒 Adding to cart: Product ID {product_id}, Quantity {quantity}")

        user_id = request.session.get('user_id')
        if not user_id or not ObjectId.is_valid(user_id):
            print("❌ User session not found or invalid user_id")
            return JsonResponse({"error": "User session not found"}, status=401)

        user_id = ObjectId(user_id)

        # Add product to cart using MongoDBCart class
        result = MongoDBCart.add_to_cart(user_id, product_id, quantity)

        if not result["success"]:
            print(f"❌ Error adding to cart: {result['error']}")
            return JsonResponse({"error": result["error"]}, status=500)

        print("✅ Product successfully added to cart!")
        return JsonResponse({
            "success": True,
            "message": "Product added to cart successfully"
        })

    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        traceback.print_exc()  # Print the full error stack trace
        return JsonResponse({"error": "Internal Server Error"}, status=500)


def top_rated_products(request):
    """Fetch the top 10 highest-rated products based on average review rating."""
    
    all_products = MongoDBProduct.get_all_products()  # Fetch all products
    product_ratings = []

    for product in all_products:
        reviews = MongoDBReview.get_review_by_product_id(product["_id"])  # Get reviews for each product
        if reviews:
            avg_rating = sum(review["ReviewStars"] for review in reviews) / len(reviews)
            product_ratings.append((product, avg_rating))

    # Sort products by rating (highest first) and get top 10
    top_products = sorted(product_ratings, key=lambda x: x[1], reverse=True)[:10]

    # Return product details with ratings
    response_data = [
        {
            "product": product,
            "average_rating": round(avg_rating, 2),
        }
        for product, avg_rating in top_products
    ]

    return JsonResponse(response_data, safe=False)

@csrf_exempt
def get_latest_products(request):
    """Fetch and return the 10 latest products as JSON."""
    try:
        latest_products = MongoDBProduct.get_top_latest_products(limit=10)  # Fetch latest products
        return JsonResponse({"success": True, "products": latest_products}, status=200)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def update_cart_total_price(cart):
    total_price = 0
    for item in cart["products"]:
        product = get_product_by_id(item["product_id"])  # Helper function to get product details
        total_price += product["discounted_price"] * item["quantity"]
    
    cart_collection.update_one({"_id": cart["_id"]}, {"$set": {"total_price": total_price}})

# Place Order API
orders_collection = settings.MONGO_DB["orders"]

# @api_view(['POST'])
# def place_order(request):
#     if request.method == "POST":
#         try:
#             body = json.loads(request.body.decode('utf-8'))
#             user_id = body.get("user_id")
#             shipping_address = body.get("shipping_address")

#             if not user_id or not shipping_address:
#                 return JsonResponse({"error": "Missing required fields"}, status=400)

#             # Retrieve the user's cart
#             cart = cart_collection.find_one({"user_id": ObjectId(user_id)})

#             if not cart or not cart["products"]:
#                 return JsonResponse({"error": "Cart is empty, cannot place order"}, status=400)

#             # Create an order
#             order_data = {
#                 "user_id": ObjectId(user_id),
#                 "products": cart["products"],
#                 "order_status": "pending",
#                 "total_price": cart["total_price"],
#                 "created_at": datetime.now(),
#                 "shipping_address": shipping_address,
#             }
#             result = orders_collection.insert_one(order_data)

#             # Empty the cart after placing the order
#             cart_collection.update_one({"user_id": ObjectId(user_id)}, {"$set": {"products": [], "total_price": 0}})

#             return JsonResponse({"message": "Order placed successfully", "order_id": str(result.inserted_id)})

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     return JsonResponse({"error": "Invalid request method"}, status=405)

# Get UserCart API
@api_view(['GET'])
def get_cart(request, user_id):
    try:
        cart = cart_collection.find_one({"user_id": ObjectId(user_id)})

        if not cart:
            return JsonResponse({"error": "Cart not found"}, status=404)

        return JsonResponse({
            "cart": cart
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Get Orders API
@api_view(['GET'])
def get_orders(request, user_id):
    try:
        orders = orders_collection.find({"user_id": ObjectId(user_id)})

        order_list = []
        for order in orders:
            order_data = {
                "order_id": str(order["_id"]),
                "products": order["products"],
                "order_status": order["order_status"],
                "total_price": order["total_price"],
                "created_at": order["created_at"],
                "shipping_address": order["shipping_address"],
            }
            order_list.append(order_data)

        return JsonResponse({"orders": order_list})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def add_sample_products():
    try:
        # Sample products data
        sample_products = [
            {
                "name": "Premium Leather Jacket",
                "category": "Men's Clothing",
                "description": "Luxurious leather jacket with premium stitching and comfortable fit. Perfect for all seasons.",
                "price": 299.99,
                "discounted_price": 249.99,
                "stock": 25,
                "image_url": "{% static 'images/product_1.jpg' %}",
                "image_url_alt": "{% static 'images/product_1-1.jpg' %}",
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "rating": 5,
                "reviews_count": 0,
                "reviews": []
            },
            {
                "name": "Classic Denim Jeans",
                "category": "Men's Clothing",
                "description": "Classic fit denim jeans with perfect comfort and style.",
                "price": 89.99,
                "discounted_price": 79.99,
                "stock": 50,
                "image_url": "{% static 'images/product_2.jpg' %}",
                "image_url_alt": "{% static 'images/product_2-1.jpg' %}",
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "rating": 4,
                "reviews_count": 0,
                "reviews": []
            },
            {
                "name": "Cotton T-Shirt",
                "category": "Men's Clothing",
                "description": "Comfortable cotton t-shirt for everyday wear.",
                "price": 29.99,
                "discounted_price": 24.99,
                "stock": 100,
                "image_url": "{% static 'images/product_3.jpg' %}",
                "image_url_alt": "{% static 'images/product_3-1.jpg' %}",
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "rating": 5,
                "reviews_count": 0,
                "reviews": []
            }
        ]

        # Insert the products
        result = products_collection.insert_many(sample_products)
        print(f"Sample products inserted with IDs: {result.inserted_ids}")
        return result.inserted_ids

    except Exception as e:
        print(f"Error inserting sample products: {str(e)}")
        return None

# add_sample_products()
# Uncomment and run this line to add the sample products
# product_ids = add_sample_products()
# print(f"Use these IDs to test: {product_ids}")
def product_detail(request, product_id):
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        reviews = MongoDBReview.get_review_by_product_id(product_id)  # Assuming this function returns the review data

        if product:
            # Format reviews_count before sending to template
            reviews_count = product.get('reviews_count', 0)
            try:
                reviews_count = int(reviews_count)
                if reviews_count >= 1000:
                    formatted_count = f"{reviews_count/1000:.1f}k"
                else:
                    formatted_count = str(reviews_count)
            except (ValueError, TypeError):
                formatted_count = "0"


            sorted_reviews = sorted(
                reviews,
                key=lambda x: x["Date"], 
                reverse=True  # Latest reviews come first
            )

            processed_product = {
                "id": str(product["_id"]),
                "name": product.get("name", ""),
                "category": MongoDBCategory.get_category_by_id(str(product.get("category_id", ""))).get("CategoryName", ""),
                "subcategory": product.get("subcategory", ""),
                "price": product.get("price", 0),
                "stock": product.get("stock", 0),
                "variants": product.get("variants", {}),  # Fetching variants (color, size)
                "tags": product.get("tags", []),  # Fetching product tags
                "description": MongoDBDescription.get_description_by_product_id(str(product["_id"])).get("description", "fuck"),
                "reviews": sorted_reviews,  # Sorted reviews by date (newest first)
                "weight": product.get("weight", ""),
                "dimensions": product.get("dimensions", {}),  # Fetching dimensions (length, height, width)
                "images": product.get("images", []),  # List of image dictionaries (main & alt)
                "banner_img": product.get("banner_img", {"Url": "", "alt": ""})  # Banner image details
            }


            # Get cart data if user is authenticated
            cart_items = []
            cart_total = 0
            cart_items_count = 0

            if request.user.is_authenticated:
                user_id = request.session.get('user_id')
                if user_id:
                    cart = cart_collection.find_one({"user_id": ObjectId(user_id)})
                    if cart:
                        for item in cart.get("products", []):
                            try:
                                cart_product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
                                if cart_product:
                                    price = float(cart_product.get("discounted_price") or cart_product.get("price", 0))
                                    item_total = price * item["quantity"]
                                    cart_total += item_total

                                    cart_items.append({
                                        "product": {
                                            "id": str(cart_product["_id"]),
                                            "name": cart_product["name"],
                                            "image": {
                                                "url": cart_product["image_url"]
                                            },
                                            "price": price
                                        },
                                        "quantity": item["quantity"],
                                        "get_total_price": "{:.2f}".format(item_total)
                                    })
                            except Exception as e:
                                print(f"Error processing cart item: {str(e)}")
                                continue

                        cart_items_count = sum(item["quantity"] for item in cart.get("products", []))

            # Get related products (same category)
            related_products = list(products_collection.find(
                {
                    "category": product["category_id"],
                    "_id": {"$ne": ObjectId(product_id)}
                }
            ).limit(4))

            # Process related products
            processed_related_products = []
            for related in related_products:
                processed_related_products.append({
                    "id": str(related["_id"]),
                    "name": related.get("name", ""),
                    "price": related.get("price", 0),
                    "discounted_price": related.get("discounted_price", 0),
                    "image_url": related.get("image_url", ""),
                    "stock": related.get("stock", 0)
                })

            for review in reviews:
                user = MongoDBUser.get_user_by_id(review["UID"])  # Fetch user by UID
                review["UID"] = user["username"] if user else "Unknown User"  # Replace UID with username
           
            context = {
                "product": processed_product,
                "cart_items": cart_items,
                "cart_total": "{:.2f}".format(cart_total),
                "cart_items_count": cart_items_count,
                "related_products": processed_related_products,
                "reviews": sorted_reviews,  # The reviews are passed here as well
            }

            print("Context data:", context)  # Debug print

            return render(request, "USER/product_detail.html", context)
        else:
            raise Http404("Product not found")

    except Exception as e:
        print(f"Error in product_detail: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return render(request, "error.html", {"message": "Unable to fetch product details"})

def add_review(request, product_id):
    if request.method == 'POST':
        try:
            print("Received review submission for product:", product_id)  # Debug print
            
            # Get the form data
            rating = int(request.POST.get('rating', 0))
            review_text = request.POST.get('review_text', '')

            # Get the user ID from the session
            user_id = request.session.get('user_id')

            if not user_id:
                messages.error(request, 'You must be logged in to submit a review.')
                return redirect('product_detail', product_id=product_id)

            # Save review using MongoDBReview class
            review_id = MongoDBReview.add_review(product_id, user_id, review_text, rating)

            if review_id:
                messages.success(request, 'Your review has been submitted successfully!')
            else:
                messages.error(request, 'Failed to submit review. Please try again.')

        except Exception as e:
            print(f"Error adding review: {str(e)}")  # Debug print
            messages.error(request, 'An error occurred while submitting your review.')

    return redirect('product_detail', product_id=product_id)


@login_required
def admin_contact_messages(request):
    try:
        messages_list = db.contact_messages.find().sort("created_at", -1)
        context = {
            "messages": messages_list
        }
        return render(request, "admin/contact_messages.html", context)
    except Exception as e:
        print(f"Error fetching contact messages: {str(e)}")
        messages.error(request, 'Error fetching messages')
        return redirect('admin_dashboard')

@login_required
def get_cart_items(request):
    """Get cart items for the current user"""
    try:
        print("Getting cart items for user:", request.user.id)  # Debug print
        
        # Get user's cart
        cart = cart_collection.find_one({"user_id": ObjectId(str(request.user.id))})
        print("Found cart:", cart)  # Debug print
        
        if not cart:
            print("No cart found, returning empty data")  # Debug print
            return JsonResponse({
                "cart_items": [],
                "cart_total": 0
            })

        # Get product details for each cart item
        cart_items = []
        cart_total = 0
        
        for item in cart.get("products", []):
            print(f"Processing cart item: {item}")  # Debug print
            product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
            if product:
                item_total = float(product["discounted_price"]) * item["quantity"]
                cart_total += item_total
                
                cart_items.append({
                    "id": str(item["product_id"]),
                    "product": {
                        "id": str(product["_id"]),
                        "name": product["name"],
                        "image": {
                            "url": product["image_url"]
                        },
                        "price": product["discounted_price"]
                    },
                    "quantity": item["quantity"],
                    "color": item.get("color"),
                    "size": item.get("size"),
                    "total_price": item_total
                })

        response_data = {
            "cart_items": cart_items,
            "cart_total": cart_total
        }
        print("Returning cart data:", response_data)  # Debug print
        return JsonResponse(response_data)

    except Exception as e:
        print(f"Error in get_cart_items: {str(e)}")  # Debug print
        print(f"Error type: {type(e)}")  # Debug print
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Detailed error trace
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_quantity(request):
    try:
        data = request.data
        product_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity < 1:
            return JsonResponse({"error": "Quantity must be at least 1"}, status=400)
            
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"error": "User session not found"}, status=401)
            
        # Update cart
        cart = cart_collection.find_one_and_update(
            {
                "user_id": ObjectId(user_id),
                "products.product_id": product_id
            },
            {
                "$set": {
                    "products.$.quantity": quantity,
                    "updated_at": datetime.now(ist)
                }
            },
            return_document=True
        )
        
        if not cart:
            return JsonResponse({"error": "Item not found in cart"}, status=404)
            
        # Calculate totals
        cart_total = 0
        item_total = 0
        
        for item in cart.get("products", []):
            product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
            if product:
                price = float(product.get("discounted_price") or product.get("price", 0))
                if item["product_id"] == product_id:
                    item_total = price * quantity
                cart_total += price * item["quantity"]
        
        return JsonResponse({
            "success": True,
            "item_total": "{:.2f}".format(item_total),
            "cart_total": "{:.2f}".format(cart_total),
            "cart_items_count": sum(item["quantity"] for item in cart.get("products", []))
        })
        
    except Exception as e:
        print(f"Error updating cart quantity: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['POST', 'DELETE'])  # Allow DELETE method
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id=None):  # Accept product_id from URL
    try:
        # If DELETE request, get product_id from URL instead of request body
        if request.method == "DELETE":
            if not product_id:
                return JsonResponse({"error": "Product ID is required"}, status=400)
        else:  # For POST requests, get product_id from request body
            data = request.data
            product_id = data.get('item_id')

        if not product_id:
            return JsonResponse({"error": "Product ID is required"}, status=400)

        # Get user's MongoDB ID from session
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"error": "User session not found"}, status=401)

        # Remove item from cart
        removed = MongoDBCart.remove_from_cart(user_id, product_id)
        if not removed:
            return JsonResponse({"error": "Item not found in cart"}, status=404)

        # Get updated cart details
        cart = MongoDBCart.get_user_cart(user_id)
        cart_items = []
        cart_total = 0

        if cart:
            for item in cart.get("products", []):
                product = db["products"].find_one({"_id": ObjectId(item["product_id"])})
                if product:
                    price = float(product.get("discounted_price") or product.get("price", 0))
                    item_total = price * item["quantity"]
                    cart_total += item_total

                    cart_items.append({
                        "product": {
                            "id": str(product["_id"]),
                            "name": product["name"],
                            "image": {"url": product.get("image_url", "")},
                            "price": price
                        },
                        "quantity": item["quantity"],
                        "total_price": "{:.2f}".format(item_total)
                    })

        return JsonResponse({
            "success": True,
            "message": "Item removed from cart successfully",
            "cart_items": cart_items,
            "cart_total": "{:.2f}".format(cart_total),
            "cart_items_count": len(cart_items)
        })

    except Exception as e:
        import traceback
        print(f"Error removing item from cart: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({"error": str(e)}, status=500)

def cart(request):
    """Render cart page"""
    try:
        print("Cart view accessed")  # Debug print
        print(request.user.is_authenticated)
        if not request.user.is_authenticated:
            messages.error(request, "Please login to view your cart")
            return redirect('login_user')

        # Get MongoDB user ID from session
        user_id = request.session.get('user_id')
        print(f"MongoDB User ID from session: {user_id}")  # Debug print
        
        if not user_id:
            messages.error(request, "User session not found")
            return redirect('login_user')

        # Get cart data
        cart_items = []
        cart_total = 0
        
        try:
            cart = cart_collection.find_one({"user_id": ObjectId(user_id)})
            print(f"Found cart: {cart}")  # Debug print
            
            if cart:
                for item in cart.get("products", []):
                    product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
                    if product:
                        price = float(product.get("discounted_price") or product.get("price", 0))
                        item_total = price * item["quantity"]
                        cart_total += item_total
                        
                        cart_items.append({
                            "id": str(item["product_id"]),
                            "product": {
                                "id": str(product["_id"]),
                                "name": product["name"],
                                "image": {
                                    "url": product["images"][0]
                                },
                                "price": price
                            },
                            "quantity": item["quantity"],
                            "total_price": "{:.2f}".format(item_total)
                        })
        
            context = {
                "cart_items": cart_items,
                "cart_total": "{:.2f}".format(cart_total),
                "cart_items_count": len(cart_items)
            }
            
            print("Context:", context)  # Debug print
            return render(request, "USER/Bag.html", context)


        except Exception as cart_error:
            print(f"Error processing cart: {str(cart_error)}")
            print(f"Error type: {type(cart_error)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f"Error loading cart: {str(cart_error)}")
            return redirect('index')

    except Exception as e:
        print(f"Error in cart view: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        messages.error(request, f"Error loading cart: {str(e)}")
        return redirect('index')

def add_sample_cart():
    try:
        # Get an existing product from the database
        product = products_collection.find_one()
        if not product:
            print("No products found in database")
            return None

        # Create a sample cart
        sample_cart = {
            "user_id": ObjectId("65f7f7d2b67e31e2c5b0b123"),  # Replace with your test user ID
            "products": [
                {
                    "product_id": str(product["_id"]),
                    "quantity": 2,
                    "color": "Black",
                    "size": "L"
                }
            ],
            "created_at": datetime.now(ist),
            "updated_at": datetime.now(ist)
        }

        # Insert the sample cart
        result = cart_collection.insert_one(sample_cart)
        print("Sample cart created with ID:", str(result.inserted_id))
        return str(result.inserted_id)

    except Exception as e:
        print(f"Error creating sample cart: {str(e)}")
        return None

# Run this to create the sample cart
# cart_id = add_sample_cart()
# print(f"Created cart with ID: {cart_id}")

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    if request.method == 'GET':
        return render(request, 'USER/password_reset.html')
        
    elif request.method == 'POST':
        try:
            email = request.data.get('email')
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Please provide an email address.'
                }, status=400)

            # Find user in MongoDB
            user = users_collection.find_one({"email": email})
            if not user:
                return JsonResponse({
                    'success': True,
                    'message': 'If an account exists with this email, you will receive password reset instructions.'
                })

            # Get Django user
            django_user = User.objects.get(email=email)

            # Generate token
            token = default_token_generator.make_token(django_user)
            uid = urlsafe_base64_encode(force_bytes(django_user.pk))

            # Build reset URL
            current_site = get_current_site(request)
            reset_url = reverse('password_reset_confirm', kwargs={
                'uidb64': uid,
                'token': token
            })
            reset_url = f"{request.scheme}://{current_site.domain}{reset_url}"

            # Email context
            context = {
                'user': django_user,
                'protocol': request.scheme,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
                'reset_url': reset_url,
            }

            # Send email
            try:
                email_subject = render_to_string('USER/password_reset_subject.txt')
                email_body = render_to_string('USER/password_reset_email.html', context)
                
                send_mail(
                    subject=email_subject.strip(),
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Password reset instructions have been sent to your email.'
                })
                
            except Exception as e:
                print(f"Email sending error: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to send password reset email. Please try again later.'
                }, status=500)

        except Exception as e:
            print(f"Password reset error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again later.'
            }, status=500)

def get_csrf_token(request):
    return JsonResponse({'csrf_token': get_token(request)})



def admin_dashboard(request):
    return render(request, 'Admin/admin-Dashboard.html')

def customer_chat(request):
    return render(request, 'Admin/CustomerChat.html')

def customer_details(request):
    return render(request, 'Admin/CustomerDetails.html')

def customers_list(request):
    return render(request, 'Admin/CustomersList.html')

def customer_stats(request):
    return render(request, 'Admin/CustomerStats.html')

def login_dashboard(request):
    return render(request, 'Admin/LoginDashoard.html')

def orders_detail(request):
    return render(request, 'Admin/OrdersDetail.html')

def orders_list(request):
    return render(request, 'Admin/OrdersList.html')


@login_required
def test_view(request):
    return JsonResponse({"message": "You are logged in!"})


def editBanners(request):
    return render(request, 'Admin/editBanners.html')

def productsList(request):
    return render(request, 'Admin/productsList.html')
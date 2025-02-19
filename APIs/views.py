from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from APIs.mongodb import MongoDBUser, MongoDBReview,MongoDBDescription,MongoDBCategory,MongoDBProduct    # Import MongoDB Helper
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
# from .mongodb.MongoDBProduct import MongoDBProduct
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
    """Home Page View - Fetch products, categories, and cart details."""
    try:
        print("\n🔹 Index View Debugging 🔹")
        user_id = request.session.get('user_id')
        print(f"User ID from session: {user_id}")

        is_authenticated = request.user.is_authenticated
        print(f"Is user authenticated? {is_authenticated}")

        # ✅ Fetch & Serialize Products (Filtering Invalid Entries)
        def fetch_and_serialize_products(query={}):
            """Fetch products from DB and ensure valid serialization."""
            products = list(products_collection.find(query))
            serialized_products = [MongoDBProduct.serialize_product(p) for p in products]
            return [p for p in serialized_products if p is not None]  # Remove empty IDs

        processed_products = fetch_and_serialize_products({})
        new_arrivals = fetch_and_serialize_products({"is_new_arrival": True})
        best_sellers = fetch_and_serialize_products({"is_best_seller": True})
        top_rated = fetch_and_serialize_products({"is_top_rated": True})

        # ✅ Debugging: Print Product IDs

       
        for product in processed_products:
            print(f"✔ Product: {product['name']} | ID: {product['id']}")

        # ✅ Cart Data
        cart_items = []
        cart_total = 0

        if is_authenticated and user_id:
            print(f"🛒 Fetching cart for MongoDB user_id: {user_id}")
            cart = cart_collection.find_one({"user_id": ObjectId(user_id)})

            if cart:
                for item in cart.get("products", []):
                    try:
                        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
                        if product:
                            price = float(product.get("discounted_price") or product.get("price", 0))
                            quantity = item["quantity"]
                            item_total = price * quantity
                            cart_total += item_total

                            cart_items.append({
                                "id": str(product["_id"]),
                                "product": {
                                    "id": str(product["_id"]),
                                    "name": product["name"],
                                    "image": {"url": product.get("image_url", "")},
                                    "price": price
                                },
                                "quantity": quantity,
                                "color": item.get("color"),
                                "size": item.get("size"),
                                "get_total_price": "{:.2f}".format(item_total)
                            })
                    except Exception as e:
                        print(f"⚠️ Error processing product: {e}")
                        continue

        # ✅ Pass Context to Template
        context = {
            "user": request.user,
            "products": processed_products,
            "new_arrivals": new_arrivals,
            "best_sellers": best_sellers,
            "top_rated": top_rated,
            "categories": list(products_collection.distinct("category")),
            "cart_items": cart_items,
            "cart_total": "{:.2f}".format(cart_total),
            "cart_items_count": len(cart_items),
        }

        return render(request, "Home/index.html", context)

    except Exception as e:
        print(f"❌ Error in index view: {str(e)}")
        import traceback
        print(traceback.format_exc())

        return render(request, "Home/index.html", {
            "message": "Unable to fetch products",
            "cart_items": [],
            "cart_total": "0.00",
            "cart_items_count": 0
        })


def acc_details(request):
    return render(request, 'USER/Acc_details.html')

def address(request):
    return render(request, 'USER/Address.html')

def checkout(request):
    return render(request, 'USER/CheckOut.html')

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

@login_required
def item_sort(request):
    try:
        # Get filter parameters from request
        category = request.GET.get('category')
        sort_by = request.GET.get('sort_by', 'price')  # Default sort by price
        order = request.GET.get('order', 'asc')  # Default ascending order
        
        # Base query
        query = {}
        
        # Add category filter if specified
        if category:
            query['category'] = category
            
        # Get products from MongoDB
        if order == 'asc':
            products = products_collection.find(query).sort(sort_by, 1)
        else:
            products = products_collection.find(query).sort(sort_by, -1)
            
        # Convert MongoDB cursor to list and process products
        products_list = []
        for product in products:
            products_list.append({
                'id': str(product['_id']),
                'name': product.get('name', ''),
                'price': product.get('price', 0),
                'image': product.get('image', ''),
                'category': product.get('category', ''),
                'description': product.get('description', ''),
                'in_stock': product.get('in_stock', True)
            })
            
        # Get all unique categories for filter dropdown
        categories = products_collection.distinct('category')
            
        context = {
            'products': products_list,
            'categories': categories,
            'selected_category': category,
            'sort_by': sort_by,
            'order': order
        }
        
        return render(request, 'USER/Item-Sort.html', context)
        
    except Exception as e:
        print(f"Error in item_sort view: {str(e)}")
        return render(request, 'USER/Item-Sort.html', {
            'products': [],
            'categories': [],
            'error_message': 'Unable to fetch products'
        })



def orders(request):
    return render(request, 'USER/Orders.html')

# def product_item(request):
#     return render(request, 'USER/product-Item.html')

@login_required
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

@api_view(['POST'])
@csrf_exempt
def add_product(request):
    """API endpoint to add a new product using MongoDBProduct class."""
    if request.method == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))

            # Extract fields from request body
            name = body.get("name")
            category_id = body.get("category_id")
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
            if not name or not category_id or not actual_price or not price:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Call MongoDBProduct method to insert the product
            product_id = MongoDBProduct.add_product(
                name=name,
                category_id=category_id,
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
from datetime import datetime
from django.conf import settings
import json
from bson import ObjectId
from .permissions import IsMongoAuthenticated 

# MongoDB collections
cart_collection = settings.MONGO_DB["cart"]

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes


@api_view(['POST'])
@permission_classes([IsMongoAuthenticated])  # Use custom MongoDB auth check
def add_to_cart(request):
    print(f"🚀 Before Auth Check: request.user = {request.user}")

    if not request.user.is_authenticated:
        print("❌ Authentication Failed: User is Anonymous")
        return JsonResponse({"redirect": "/login"}, status=401)

    print("✅ User Authenticated, Proceeding to add to cart")
    try:
        data = request.data
        product_id = data.get('product_id')

        # Get quantity with proper error handling
        try:
            quantity = int(data.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1

        print(f"Adding to cart: Product ID {product_id}, Quantity {quantity}")

        if not product_id:
            return JsonResponse({"error": "Product ID is required"}, status=400)

        # Verify product exists and has enough stock
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return JsonResponse({"error": "Product not found"}, status=404)

        stock = product.get('stock', 0)
        if stock < quantity:
            return JsonResponse({
                "error": f"Not enough stock. Only {stock} items available."
            }, status=400)

        # Get user's MongoDB ID from session
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"error": "User session not found"}, status=401)

        # Find user's cart
        cart = cart_collection.find_one({"user_id": ObjectId(user_id)})

        if cart:
            # Check if product already exists in cart
            product_exists = False
            products = cart.get("products", [])
            for item in products:
                if str(item["product_id"]) == str(product_id):
                    new_quantity = item["quantity"] + quantity
                    if new_quantity > stock:
                        return JsonResponse({
                            "error": f"Cannot add {quantity} more items. Only {stock - item['quantity']} items available."
                        }, status=400)
                    item["quantity"] = new_quantity
                    product_exists = True
                    break

            if not product_exists:
                products.append({
                    "product_id": product_id,
                    "quantity": quantity
                })

            # Update cart in database
            result = cart_collection.update_one(
                {"user_id": ObjectId(user_id)},
                {
                    "$set": {
                        "products": products,
                        "updated_at": datetime.now()
                    }
                }
            )
        else:
            # Create new cart
            new_cart = {
                "user_id": ObjectId(user_id),
                "products": [{
                    "product_id": product_id,
                    "quantity": quantity
                }],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            result = cart_collection.insert_one(new_cart)

        return JsonResponse({
            "success": True,
            "message": "Product added to cart successfully"
        })

    except Exception as e:
        print(f"Error adding to cart: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

def update_cart_total_price(cart):
    total_price = 0
    for item in cart["products"]:
        product = get_product_by_id(item["product_id"])  # Helper function to get product details
        total_price += product["discounted_price"] * item["quantity"]
    
    cart_collection.update_one({"_id": cart["_id"]}, {"$set": {"total_price": total_price}})

# Place Order API
orders_collection = settings.MONGO_DB["orders"]

@api_view(['POST'])
def place_order(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))
            user_id = body.get("user_id")
            shipping_address = body.get("shipping_address")

            if not user_id or not shipping_address:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Retrieve the user's cart
            cart = cart_collection.find_one({"user_id": ObjectId(user_id)})

            if not cart or not cart["products"]:
                return JsonResponse({"error": "Cart is empty, cannot place order"}, status=400)

            # Create an order
            order_data = {
                "user_id": ObjectId(user_id),
                "products": cart["products"],
                "order_status": "pending",
                "total_price": cart["total_price"],
                "created_at": datetime.now(),
                "shipping_address": shipping_address,
            }
            result = orders_collection.insert_one(order_data)

            # Empty the cart after placing the order
            cart_collection.update_one({"user_id": ObjectId(user_id)}, {"$set": {"products": [], "total_price": 0}})

            return JsonResponse({"message": "Order placed successfully", "order_id": str(result.inserted_id)})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

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

            # Process product data
            processed_product = {
                "id": str(product["_id"]),
                "name": product.get("name", ""),
                "category": MongoDBCategory.get_category_by_id(str(product.get("category_id", ""))).get("CategoryName", ""),
                "subcategory": product.get("subcategory", ""),
                "price": product.get("price", 0),
                "stock": product.get("stock", 0),
                "variants": product.get("variants", {}),  # Fetching variants (color, size)
                "tags": product.get("tags", []),  # Fetching product tags
                "description": MongoDBDescription.get_description_by_product_id(str(product["_id"])).get("description", ""),
                "reviews": product.get("reviewsDictionary", []),  # Storing review IDs
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
                "reviews": reviews,  # The reviews are passed here as well
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    try:
        data = request.data
        product_id = data.get('item_id')
        
        print(f"Removing from cart: Product ID {product_id}")  # Debug print
        
        if not product_id:
            return JsonResponse({"error": "Product ID is required"}, status=400)
            
        # Get user's MongoDB ID from session
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"error": "User session not found"}, status=401)
            
        # Verify product exists
        try:
            product = products_collection.find_one({"_id": ObjectId(product_id)})
        except Exception as e:
            print(f"Error converting product_id to ObjectId: {str(e)}")
            return JsonResponse({"error": "Invalid product ID"}, status=400)
            
        if not product:
            return JsonResponse({"error": "Product not found"}, status=404)
            
        # Remove item from cart
        result = cart_collection.update_one(
            {"user_id": ObjectId(user_id)},
            {
                "$pull": {
                    "products": {"product_id": product_id}
                },
                "$set": {
                    "updated_at": datetime.now(ist)
                }
            }
        )
        
        if result.modified_count == 0:
            return JsonResponse({"error": "Item not found in cart"}, status=404)
            
        # Get updated cart data
        cart = cart_collection.find_one({"user_id": ObjectId(user_id)})
        cart_total = 0
        cart_items = []
        
        if cart:
            for item in cart.get("products", []):
                try:
                    product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
                    if product:
                        price = float(product.get("discounted_price") or product.get("price", 0))
                        item_total = price * item["quantity"]
                        cart_total += item_total
                        
                        cart_items.append({
                            "product": {
                                "id": str(product["_id"]),
                                "name": product["name"],
                                "image": {
                                    "url": product["image_url"]
                                },
                                "price": price
                            },
                            "quantity": item["quantity"],
                            "total_price": "{:.2f}".format(item_total)
                        })
                except Exception as e:
                    print(f"Error processing cart item: {str(e)}")
                    continue
        
        return JsonResponse({
            "success": True,
            "message": "Item removed from cart successfully",
            "cart_items": cart_items,
            "cart_total": "{:.2f}".format(cart_total),
            "cart_items_count": len(cart_items)
        })
        
    except Exception as e:
        print(f"Error removing item from cart: {str(e)}")
        import traceback
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
                                    "url": [img["main"] for img in product["imagesDictionary"]]
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


# @login_required
from django.http import JsonResponse
from django.conf import settings
from bson import ObjectId
import datetime

def test_view(request):
    """ Inserts sample product data into MongoDB """
    
    # ✅ Connect to MongoDB
    products_collection = settings.MONGO_DB["products"]

    # ✅ Sample Product Data with Different Filters
    products_data = [
        {
            "_id": ObjectId(),
            "name": "Premium Leather Jacket",
            "added_date": datetime.datetime.utcnow(),
            "updated_date": datetime.datetime.utcnow(),
            "category_id": ObjectId(),
            "subcategory": "Men's Jackets",
            "actual_price": 299.99,
            "price": 249.99,
            "discount_percentage": 17,
            "stock": 15,
            "variants": {
                "color": { "black": 7, "brown": 8 },
                "size": { "M": 5, "L": 10 }
            },
            "tags": ["leather", "jacket", "men", "fashion"],
            "description_id": ObjectId(),
            "reviews": [ObjectId()],
            "weight": "1.5kg",
            "dimensions": { "length": "70cm", "width": "50cm", "height": "10cm" },
            "images": [
                { "main": "leather_jacket_black.jpg", "alt": "leather_jacket_alt.jpg" },
                { "main": "leather_jacket_brown.jpg", "alt": "leather_jacket_brown_alt.jpg" }
            ],
            "banner_img": { "Url": "leather_jacket_banner.jpg", "alt": "Premium Leather Jacket" },
            "is_new_arrival": False,
            "is_best_seller": True,
            "is_top_rated": True,
            "rating": 4.8,
            "sales_count": 450,
            "available_colors": ["Black", "Brown"],
            "available_sizes": ["M", "L"]
        },

        {
            "_id": ObjectId(),
            "name": "Smart Casual Sneakers",
            "added_date": datetime.datetime.utcnow(),
            "updated_date": datetime.datetime.utcnow(),
            "category_id": ObjectId(),
            "subcategory": "Men's Shoes",
            "actual_price": 89.99,
            "price": 69.99,
            "discount_percentage": 22,
            "stock": 25,
            "variants": {
                "color": { "white": 10, "blue": 15 },
                "size": { "8": 5, "9": 10, "10": 10 }
            },
            "tags": ["sneakers", "casual", "shoes", "men"],
            "description_id": ObjectId(),
            "reviews": [ObjectId(), ObjectId()],
            "weight": "800g",
            "dimensions": { "length": "30cm", "width": "12cm", "height": "10cm" },
            "images": [
                { "main": "sneakers_white.jpg", "alt": "casual_sneakers_alt.jpg" },
                { "main": "sneakers_blue.jpg", "alt": "sneakers_blue_alt.jpg" }
            ],
            "banner_img": { "Url": "sneakers_banner.jpg", "alt": "Smart Casual Sneakers" },
            "is_new_arrival": True,
            "is_best_seller": False,
            "is_top_rated": False,
            "rating": 4.2,
            "sales_count": 200,
            "available_colors": ["White", "Blue"],
            "available_sizes": ["8", "9", "10"]
        },

        {
            "_id": ObjectId(),
            "name": "Elegant Party Dress",
            "added_date": datetime.datetime.utcnow(),
            "updated_date": datetime.datetime.utcnow(),
            "category_id": ObjectId(),
            "subcategory": "Women's Dresses",
            "actual_price": 149.99,
            "price": 119.99,
            "discount_percentage": 20,
            "stock": 20,
            "variants": {
                "color": { "red": 10, "blue": 10 },
                "size": { "S": 5, "M": 7, "L": 8 }
            },
            "tags": ["dress", "women", "party", "elegant"],
            "description_id": ObjectId(),
            "reviews": [ObjectId()],
            "weight": "500g",
            "dimensions": { "length": "120cm", "width": "40cm", "height": "5cm" },
            "images": [
                { "main": "party_dress_red.jpg", "alt": "elegant_dress_alt.jpg" },
                { "main": "party_dress_blue.jpg", "alt": "party_dress_blue_alt.jpg" }
            ],
            "banner_img": { "Url": "party_dress_banner.jpg", "alt": "Elegant Party Dress" },
            "is_new_arrival": True,
            "is_best_seller": False,
            "is_top_rated": True,
            "rating": 4.9,
            "sales_count": 350,
            "available_colors": ["Red", "Blue"],
            "available_sizes": ["S", "M", "L"]
        },

        {
            "_id": ObjectId(),
            "name": "Ultra Comfort Hoodie",
            "added_date": datetime.datetime.utcnow(),
            "updated_date": datetime.datetime.utcnow(),
            "category_id": ObjectId(),
            "subcategory": "Men's Hoodies",
            "actual_price": 79.99,
            "price": 59.99,
            "discount_percentage": 25,
            "stock": 30,
            "variants": {
                "color": { "gray": 15, "black": 15 },
                "size": { "M": 10, "L": 20 }
            },
            "tags": ["hoodie", "men", "fashion", "casual"],
            "description_id": ObjectId(),
            "reviews": [ObjectId()],
            "weight": "1.2kg",
            "dimensions": { "length": "70cm", "width": "50cm", "height": "15cm" },
            "images": [
                { "main": "hoodie_gray.jpg", "alt": "hoodie_alt.jpg" },
                { "main": "hoodie_black.jpg", "alt": "hoodie_black_alt.jpg" }
            ],
            "banner_img": { "Url": "hoodie_banner.jpg", "alt": "Ultra Comfort Hoodie" },
            "is_new_arrival": False,
            "is_best_seller": True,
            "is_top_rated": False,
            "rating": 4.5,
            "sales_count": 275,
            "available_colors": ["Gray", "Black"],
            "available_sizes": ["M", "L"]
        }
    ]

    # ✅ Insert data into MongoDB
    insert_result = products_collection.insert_many(products_data)
    print(f"Inserted {len(insert_result.inserted_ids)} products successfully!")

    return JsonResponse({"message": f"Inserted {len(insert_result.inserted_ids)} products successfully!"})


def add_product(request):
    return render(request, 'Admin/add-product.html')

def editBanners(request):
    return render(request, 'Admin/editBanners.html')

def productsList(request):
    return render(request, 'Admin/productsList.html')
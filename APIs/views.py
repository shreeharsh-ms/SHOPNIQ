from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from APIs.mongodb import MongoDBUser  # Import MongoDB Helper
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

# Y2qK9yW21YLMQCUT
# daredevilgamerdream

ist = pytz.timezone('Asia/Kolkata')

# MongoDB setup
client = pymongo.MongoClient("mongodb+srv://shree:Y2qK9yW21YLMQCUT@cluster0.4evpu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client["shopniq_db"]
login_sessions = db["login_sessions"]

try:
    # Test MongoDB connection
    products_collection = db["products"]
    
    # Try to fetch one product
    test_product = products_collection.find_one()
    print("Test MongoDB Connection:", test_product)
except Exception as e:
    print("MongoDB Connection Error:", str(e))


@csrf_exempt
@api_view(['POST'])
def login_user(request):
    data = request.data
    email = data.get("login_email")
    password = data.get("login_password")

    user = MongoDBUser.get_user_by_email(email)

    if user and check_password(password, user.get("password")):
        session_data = {
            "user_id": str(user["_id"]),
            "email": email,
            "ip_address": get_client_ip(request),
            "user_agent": request.headers.get("User-Agent"),
            "login_time": datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S"),
            "logout_time": None  # Initially None
        }
        
        session_id = login_sessions.insert_one(session_data).inserted_id

        # You could send a redirect or a response depending on your app needs
        messages.success(request, "Login successful!")
        return redirect('index')  # Ensure 'index' URL pattern exists or change accordingly
    else:
        return Response({"error": "Invalid email or password"}, status=400)


def get_client_ip(request):
    """Extract the client IP address from the request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

@api_view(['POST'])  # Typically, logout is a POST request
def logout_user(request):
    # Get the session_id from the request data (can also be from URL or headers if needed)
    session_id = request.data.get("session_id")  # Ensure the key matches what you send from the frontend
    print(session_id)
    # Check if session_id is provided
    if not session_id:
        return Response({"error": "Session ID required"}, status=400)

    try:
        # Update logout time in MongoDB using the session_id
        result = login_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"logout_time": datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")}}  # Set the logout time
        )

        if result.modified_count == 0:
            return Response({"error": "Invalid session ID or session already logged out"}, status=400)

        # Optionally, you can also delete the session or perform other actions (e.g., cleanup)

        # Send a success message back to the client
        messages.success(request, "Logout successful!")
        return Response({"message": "Logout successful!"}, status=200)
        # messages.success(request, "Logout successful!")
        # return redirect('register_page')  # Ensure 'index' URL pattern exists or change accordingly

    except Exception as e:
        # If there's an error (e.g., MongoDB connection issue)
        return Response({"error": str(e)}, status=500)

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
@csrf_exempt
@api_view(['POST'])
def register_user(request):
    data = request.data

    if MongoDBUser.get_user_by_email(data.get("email")):
        return Response({"error": "User already exists"}, status=400)

    # Create new user
    user = MongoDBUser.create_user(data.get("username"), data.get("email"), data.get("password"))

    messages.success(request, "Registration successful! Please log in.")
    
    # Redirect to login page or send an appropriate response
    return redirect('login')  # Adjust the URL pattern accordingly



def register_page(request):
    return render(request, 'REGISTER/register.html')


def index(request):
    print("Index view called!")  # Debug print 1
    try:
        # Fetch all active products and sort by date
        print("Attempting to fetch products...")  # Debug print 2
        products = list(products_collection.find())
        print("Raw products from DB:", products)  # Debug print 3

        # Process each product
        processed_products = []
        for product in products:
            processed_product = {
                "id": str(product["_id"]),
                "name": product.get("name", ""),
                "category": product.get("category", ""),
                "price": product.get("price", 0),
                "discounted_price": product.get("discounted_price", 0),
                "image_url": product.get("image_url", ""),
                "image_url_alt": product.get("image_url_alt", ""),
                "description": product.get("description", ""),
                "status": product.get("status", "active"),
                "created_at": product.get("created_at", ""),
                "updated_at": product.get("updated_at", "")
            }
            processed_products.append(processed_product)

        context = {
            "products": processed_products,
            "categories": list(products_collection.distinct("category"))
        }
        print("\n\n\n\n\n\n\n\nFinal context:", context)  # Debug print 4
        
        return render(request, "Home/index.html", context)
    except Exception as e:
        print(f"Error in index view: {str(e)}")  # Debug print 5
        return render(request, "Home/index.html", {"message": "Unable to fetch products"})



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

# def product_item(request):
#     return render(request, 'USER/product-Item.html')

def wishlist(request):
    return render(request, 'USER/WishList.html')

def about_us(request):
    return render(request, 'Home/ABOUTUS.html')

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
@api_view(['POST'])
@csrf_exempt
def add_product(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))
            name = body.get("name")
            description = body.get("description")
            original_price = body.get("original_price")
            discounted_price = body.get("discounted_price")
            discount = body.get("discount")
            image_url = body.get("image_url")
            stock = body.get("stock")
            category = body.get("category")

            if not name or not original_price or not discounted_price:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Product data structure
            product_data = {
                "name": name,
                "description": description,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "discount": discount,
                "image_url": image_url,
                "stock": stock,
                "category": category,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            result = products_collection.insert_one(product_data)
            return JsonResponse({"message": "Product added successfully", "product_id": str(result.inserted_id)})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# API to fetch all products from MongoDB
@api_view(['GET'])
def get_product_details(request, product_id):
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return JsonResponse({"error": "Product not found"}, status=404)

        product_data = {
            "name": product["name"],
            "description": product.get("description"),
            "original_price": product["original_price"],
            "discounted_price": product["discounted_price"],
            "discount": product["discount"],
            "image_url": product["image_url"],
            "stock": product["stock"],
            "category": product["category"],
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

# MongoDB collections
cart_collection = settings.MONGO_DB["cart"]

@api_view(['POST'])
def add_to_cart(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))
            user_id = body.get("user_id")
            product_id = body.get("product_id")
            quantity = body.get("quantity", 1)

            if not user_id or not product_id:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Find user's cart in the database
            cart = cart_collection.find_one({"user_id": ObjectId(user_id)})

            if cart:
                # If cart exists, check if the product is already in the cart
                existing_product = next((item for item in cart["products"] if item["product_id"] == product_id), None)
                if existing_product:
                    # If the product is already in the cart, update quantity
                    existing_product["quantity"] += quantity
                else:
                    # Add new product to the cart
                    cart["products"].append({"product_id": product_id, "quantity": quantity})
            else:
                # If cart does not exist, create a new cart
                cart_data = {
                    "user_id": ObjectId(user_id),
                    "products": [{"product_id": product_id, "quantity": quantity}],
                    "total_price": 0,
                }
                cart_collection.insert_one(cart_data)

            # Update the cart's total price
            update_cart_total_price(cart)
            
            return JsonResponse({"message": "Product added to cart successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

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

add_sample_products()
# Uncomment and run this line to add the sample products
# product_ids = add_sample_products()
# print(f"Use these IDs to test: {product_ids}")

def product_detail(request, product_id):
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        
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
            
            # Make sure we're passing the string version of the ObjectId
            processed_product = {
                "id": str(product["_id"]),  # Convert ObjectId to string
                "name": product.get("name", ""),
                "formatted_reviews_count": formatted_count,
                "category": product.get("category", ""),
                "price": product.get("price", 0),
                "discounted_price": product.get("discounted_price", 0),
                "image_url": product.get("image_url", ""),
                "image_url_alt": product.get("image_url_alt", ""),
                "description": product.get("description", ""),
                "status": product.get("status", "active"),
                "rating": product.get("rating", 5),
                # Add reviews to processed product
                "reviews": product.get("reviews", []),
                "reviews_count": reviews_count,
                # Add stock information
                "stock": product.get("stock", 0)
            }
            
            print("Processed product:", processed_product)  # Debug print
            
            context = {
                "product": processed_product
            }
            return render(request, "USER/product_detail.html", context)
        else:
            raise Http404("Product not found")
            
    except Exception as e:
        print(f"Error in product_detail: {str(e)}")
        return render(request, "error.html", {"message": "Unable to fetch product details"})



def add_review(request, product_id):
    if request.method == 'POST':
        try:
            print("Received review submission for product:", product_id)  # Debug print
            
            # Get the form data
            rating = int(request.POST.get('rating', 0))
            review_text = request.POST.get('review_text', '')
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            
            # Get current product to check current reviews_count
            current_product = products_collection.find_one({"_id": ObjectId(product_id)})
            current_count = current_product.get('reviews_count', 0)
            
            # Convert string count to integer if necessary
            if isinstance(current_count, str):
                try:
                    current_count = int(current_count.replace('k', '000'))
                except ValueError:
                    current_count = 0
            
            # Create the review object
            review = {
                "name": name,
                "email": email,
                "rating": rating,
                "text": review_text,
                "date": datetime.now().strftime("%B %d, %Y"),
                "avatar": None
            }
            
            # Update the product document with new review and incremented count
            result = products_collection.update_one(
                {"_id": ObjectId(product_id)},
                {
                    "$push": {"reviews": review},
                    "$set": {
                        "reviews_count": current_count + 1,
                        "updated_at": datetime.now()
                    }
                }
            )
            
            print("MongoDB update result:", result.modified_count)  # Debug print
            
            if result.modified_count > 0:
                messages.success(request, 'Your review has been submitted successfully!')
            else:
                messages.error(request, 'Failed to submit review. Please try again.')
                
        except Exception as e:
            print(f"Error adding review: {str(e)}")  # Debug print
            messages.error(request, 'An error occurred while submitting your review.')
            
    return redirect('product_detail', product_id=product_id)
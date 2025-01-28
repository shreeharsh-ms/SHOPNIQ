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


ist = pytz.timezone('Asia/Kolkata')

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["shopniq_db"]
login_sessions = db["login_sessions"]


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
    return render(request, 'Home/index.html')


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
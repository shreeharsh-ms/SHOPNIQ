from pymongo import MongoClient
import bcrypt
from SHOPNIQ.settings import MONGO_DB
from bson import ObjectId
from datetime import datetime
# client = MongoClient("mongodb://localhost:27017/")
# db = client["your_database"]
users_collection = MONGO_DB["users"]
contact_messages = MONGO_DB["contact_messages"]

class MongoDBUser:
    @staticmethod
    def create_user(username, email, password, role="user"):  # Default role = user
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": role  # Add role field
        }

        result = users_collection.insert_one(user_data)
        return result.inserted_id

    @staticmethod
    def create_user(username, email, role, password=None,):
        """ Create a new user in MongoDB. """
        existing_user = users_collection.find_one({"email": email})
        
        if existing_user:
            return existing_user  # Return existing user
        
        # Create new user
        new_user = {
            "username": username,
            "email": email,
            "password": password if password else None,  # Allow None password for Google OAuth
            "role": role,
            "date_of_register": datetime.utcnow(),
            "last_login": datetime.utcnow(),
            "session_timing": "120 min",
            "address": [],
            "orders": []
        }
        
        inserted = users_collection.insert_one(new_user)
        new_user["_id"] = inserted.inserted_id
        return new_user

    @staticmethod
    def get_user_by_email(email):
        return users_collection.find_one({"email": email})

    @staticmethod
    def get_user_by_id(user_id):
        try:
            print(f"🔍 Fetching User by ID: {user_id}")  # Debugging
            return users_collection.find_one({"_id": ObjectId(user_id)})  # ✅ Ensure ObjectId is used correctly
        except Exception as e:
            print(f"❌ Error fetching user by ID: {e}")
            return None
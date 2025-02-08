from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from bson.objectid import ObjectId
from SHOPNIQ.settings import MONGO_DB

class MongoDBUser:
    collection = MONGO_DB["users"]

    @staticmethod
    def create_user(username, email, password, role="customer"):
        hashed_password = make_password(password)
        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": role,
            "created_at": now(),
            "address": [],
            "orders": []
        }
        return MongoDBUser.collection.insert_one(user_data)

    @staticmethod
    def get_user_by_email(email):
        return MongoDBUser.collection.find_one({"email": email})

    @staticmethod
    def get_user_by_id(user_id):
        return MongoDBUser.collection.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def add_order_to_user(user_id, order_id):
        return MongoDBUser.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"orders": order_id}}
        )

contact_messages = MONGO_DB["contact_messages"]

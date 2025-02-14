from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .mongodb import MongoDBUser
from django.contrib.auth.hashers import check_password

User = get_user_model()

class MongoDBAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        user_data = MongoDBUser.get_user_by_email(email)
        if user_data and check_password(password, user_data.get("password")):
            # Create a Django user object
            user = User(
                id=user_data.get("_id"),
                username=user_data.get("username"),
                email=user_data.get("email")
            )
            return user
        return None

    def get_user(self, user_id):
        user_data = MongoDBUser.get_user_by_id(user_id)
        if user_data:
            return User(
                id=user_data.get("_id"),
                username=user_data.get("username"),
                email=user_data.get("email")
            )
        return None 
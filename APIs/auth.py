from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.backends import BaseBackend
from .mongodb import MongoDBUser
import bcrypt
from django.contrib.auth.models import AbstractBaseUser

from django.contrib.auth.models import AbstractBaseUser

class MongoUser(AbstractBaseUser):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data.get("username", "UnknownUser")
        self.email = user_data.get("email", "")
        self.role = user_data.get("role", "user")

    @property
    def is_authenticated(self):
        return True  # ✅ Ensures Django recognizes this as an authenticated user

    @property
    def is_anonymous(self):
        return False  # ✅ Prevents Django from treating it as AnonymousUser

    def __str__(self):
        return self.username



class MongoDBAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        user_data = MongoDBUser.get_user_by_email(email)
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
            return MongoUser(user_data)  # ✅ Return an instance of MongoUser
        return None

    def get_user(self, user_id):
        user_data = MongoDBUser.get_user_by_id(user_id)
        if user_data:
            return MongoUser(user_data)
        return None

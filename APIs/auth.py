from django.contrib.auth.backends import BaseBackend
from .mongodb import MongoDBUser
from django.contrib.auth.hashers import check_password


class MongoDBAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        user = MongoDBUser.get_user_by_email(email)
        if user and check_password(password, user.get("password")):
            return user
        return None

    def get_user(self, user_id):
        return MongoDBUser.get_user_by_id(user_id) 
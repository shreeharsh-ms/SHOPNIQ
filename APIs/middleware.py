from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .mongodb import MongoDBUser
from .auth import MongoUser

class MongoDBUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get("user_id")
        print(f"\n🔹 Middleware Debugging: user_id from session: {user_id}")

        if user_id:
            user_data = MongoDBUser.get_user_by_id(user_id)
            if user_data:
                request.user = MongoUser(user_data)  # ✅ Assign MongoDB user
                print(f"✅ User Successfully Loaded into request.user: {request.user}")
                return  

            else:
                print("❌ MongoDB User Not Found for ID:", user_id)

        request.user = AnonymousUser()
        print("❌ User Not Found, Using AnonymousUser")

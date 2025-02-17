from django.shortcuts import redirect
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from .mongodb import MongoDBUser
from .auth import MongoUser

class MongoDBUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print(f"🔹 Middleware Debugging: Session Data: {dict(request.session.items())}")

        user_id = request.session.get("user_id")
        print(f"🔹 Extracted user_id from session: {user_id}")

        if user_id:
            # If user_id is found in session, try to fetch the MongoDB user
            user_data = MongoDBUser.get_user_by_id(user_id)
            if user_data:
                user = MongoUser(user_data)
                request.user = user
                request._cached_user = user  # Prevent Django from overwriting user
                setattr(request, "_force_auth_user", user)  # Make sure user persists
                print(f"✅ Middleware: request.user SET as {request.user}")
            else:
                print("❌ Middleware: MongoDB User Not Found")
                request.user = AnonymousUser()
                # Redirect to login only for restricted pages like add-to-cart
                # if 'add-to-cart' in request.path:
                #     return redirect('login_view')
        else:
            print("❌ Middleware: No user_id found in session, setting AnonymousUser")
            request.user = AnonymousUser()
            # You can optionally leave this here if you need a redirect only on restricted pages
            # No redirect here to allow unauthenticated access to other pages.

    def process_response(self, request, response):
        print(f"🔹 Response Debugging: Final request.user = {request.user}")
        return response

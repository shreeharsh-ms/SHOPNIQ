# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth.models import get_user_model

# class CustomAuthBackend(ModelBackend):
#     def authenticate(self, request, email=None, password=None, **kwargs):
#         UserModel = get_user_model()
#         try:
#             user = UserModel.objects.get(email=email)
#             if user.check_password(password):
#                 return user
#         except UserModel.DoesNotExist:
#             return None
#         return None 
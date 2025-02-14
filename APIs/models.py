from django.contrib.auth.models import AbstractUser
from django.db import models
from bson import ObjectId

# Create your models here.

class CustomUser(AbstractUser):
    id = models.CharField(primary_key=True, max_length=24, default=ObjectId)

    class Meta:
        db_table = 'users'

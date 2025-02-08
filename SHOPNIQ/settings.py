from pathlib import Path
import os
from datetime import timedelta

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Enable Whitenoise for serving static files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add Whitenoise middleware here
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# Security settings
SECRET_KEY = 'django-insecure-+x8naul6gx88@97vxm+oxbbc5cc0y+-i3+ys)zvjzs=b2tq9af'
DEBUG = False  # Ensure this is False in production
ALLOWED_HOSTS = ['.vercel.app', '127.0.0.1', 'localhost']  # Add your Vercel domain here

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'APIs',
    'rest_framework',
    'django.contrib.sites',  # Required for social authentication
    'rest_framework.authtoken',
    'dj_rest_auth',
    'social_django',  # Social authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth backend
]

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the environment variables
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')



# REST Framework Auth
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT Settings
JWT_SECRET_KEY = 'Sh0pN!q#2024@Key'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(days=1)

# CORS Settings (if needed)
CORS_ALLOW_ALL_ORIGINS = True  # For development only
CORS_ALLOW_CREDENTIALS = True

SITE_ID = 1
LOGIN_URL = 'register_user'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'
ACCOUNT_AUTHENTICATED_REDIRECT_URL = '/'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

ROOT_URLCONF = 'SHOPNIQ.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SHOPNIQ.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEBUG = True

# MongoDB Connection using PyMongo
import pymongo

MONGO_CLIENT = pymongo.MongoClient("mongodb://localhost:27017/")
MONGO_DB = MONGO_CLIENT["shopniq_db"]

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 2592000   # 30 Days in seconds after 30 days user will be logged out
# SESSION_COOKIE_AGE = 10  # 24 hours in seconds

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or your email host
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'gamingrangeyt@gmail.com'  # Your email
EMAIL_HOST_PASSWORD = 'luka mtlr zkjk qzqy'  # Your email app password
DEFAULT_FROM_EMAIL = 'SHOPNIQ <gamingrangeyt@gmail.com>'

# Password Reset Settings
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour timeout for reset links

from django.core.mail import send_mail

# If you don't specify from_email, it uses DEFAULT_FROM_EMAIL
# send_mail(
#     subject='Welcome to SHOPNIQ',
#     message='Thank you for registering!',
#     from_email=DEFAULT_FROM_EMAIL,  # Uses the default
#     recipient_list=['user@example.com']
# )
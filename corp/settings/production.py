
from decouple import config

from .base import *

ALLOWED_HOSTS = ['igiti.co.rw',
                 'www.igiti.co.rw', "127.0.0.1", "localhost", '198.54.116.172']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'igityopp_corp',
        'USER': config("DB_USER", cast=str),
        'PASSWORD': config('DB_PASS'),
        'HOST': '127.0.0.1',
        'PORT': '',
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


STRIPE_PUBLISHABLE_KEY = 'LIVE KEYS'
STRIPE_SECRET_KEY = 'LIVE KEYS'

PREPEND_WWW = False
APPEND_SLASH = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


SITE_ID = 1
# DEPLOYMENT

# EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("HOST_PASS")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = '465'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
ADMINS = (('Feyton', 'info@igiti.co.rw'),)

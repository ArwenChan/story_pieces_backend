"""
Django settings for story_pieces project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import logging
import os
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


env = environ.Env(
    # DEBUG开关
    DEBUG=(bool, True),

    # 数据库配置
    REDIS_HOST=(str, 'localhost'),
    REDIS_PORT=(int, 6379),
    REDIS_DB=(int, 0),
    REDIS_PASSWORD=(str, ''),
    BROKER_URL=(str, 'redis://@127.0.0.1:6379/13'),
    RESULT_URL=(str, 'redis://@127.0.0.1:6379/14'),
    DATABASE_URL=(str, 'postgres://story:@localhost:5432/stories'),
    QINIU_KEY=(str, 'l88GdJ3sc6u480iwHcX1zGfPt3oNhH7oLz6l8lqC'),
    QINIU_SECRET=(str, 'sP_80qwrnH4vfsNoxONMLCa8JBitTyGNcE6n6hLM'),
    QINIU_IMG_BUCKET=(str, 'story-pieces'),
    QINIU_IMG_DOMAIN=(str, 'http://pj5hr98xx.bkt.clouddn.com/'),

)
environ.Env.read_env()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_q9+qme)ak0iet$xp%1^=8=fk)0$huv4zo+*hp_608c^6$n-2a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',

    'forum',
    'member',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'story_pieces.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'story_pieces.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': env.db('DATABASE_URL')
}




# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'member.User'

AUTHENTICATION_BACKENDS = (
    'story_pieces.base.authenticate_backend.MyModelBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# REST_FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'EXCEPTION_HANDLER': 'story_pieces.base.exception_handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'story_pieces.base.pagination.CustomPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'sms': '1/min',
        'default': '20/min',
    }
}

# CORS
CORS_ORIGIN_WHITELIST = (
    'localhost:9000',
    'story.arwen.space',
)
CORS_ALLOW_CREDENTIALS = True

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = default_headers + (
    'zhouyu',
)

SESSION_COOKIE_NAME = 'caocao'
SESSION_COOKIE_AGE = 3600
CSRF_HEADER_NAME = 'HTTP_ZHOUYU'
CSRF_COOKIE_NAME = 'machao'


# QINIU
QINIU_KEY = env('QINIU_KEY')
QINIU_SECRET = env('QINIU_SECRET')
QINIU_IMG_BUCKET = env('QINIU_IMG_BUCKET')
QINIU_IMG_DOMAIN = env('QINIU_IMG_DOMAIN')



# CACHE

REDIS_HOST = env('REDIS_HOST')
REDIS_PORT = env('REDIS_PORT')
REDIS_DB = env('REDIS_DB')
REDIS_PASSWORD = env('REDIS_PASSWORD')

CACHE_EXPIRE = 3 * 60 * 60

CACHES = {
    "default": {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': "redis://:%s@%s:%d/%d" % (REDIS_PASSWORD, REDIS_HOST,
                                              REDIS_PORT, REDIS_DB),
        'TIMEOUT': CACHE_EXPIRE,
        'OPTIONS': {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# CELERY

# Celery application definition
CELERY_BROKER_URL = env('BROKER_URL')
CELERY_RESULT_BACKEND = env('RESULT_URL')
CELERY_ACCEPT_CONTENT = ['pickle', 'application/json']
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'pickle'

# Sentry
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

sentry_sdk.init(
    dsn="https://fa9f19e608a448ce866b303083a6cb6f@sentry.io/1327595",
    integrations=[DjangoIntegration()],
    environment="dev" if env('DEBUG') else "prod"
)

ignore_logger("record")

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {funcName}@@{filename}:{lineno} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'story_pieces.log'),
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'record': {
            'handlers': ['file'],
            'propagate': False,
        }
    }
}




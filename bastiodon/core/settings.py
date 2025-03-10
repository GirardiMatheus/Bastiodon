import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-key-for-development')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    
    'authentication',
    'rate_limiting',
    'caching',
    'routing',
    'monitoring',

    'oauth2_provider',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'rate_limiting.middleware.RateLimitMiddleware',
    'caching.middleware.CacheMiddleware',
    'core.middlewares.RoutingMiddleware',
]

ROOT_URLCONF = 'urls'

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

WSGI_APPLICATION = 'wsgi.application'

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

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

OAUTH2_PROVIDER = {
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope'},
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 86400,
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

RATE_LIMITING = {
    'DEFAULT_LIMIT': 100,  
    'ENABLED': True,
    'CACHE_PREFIX': 'ratelimit'
}

CACHE_SETTINGS = {
    'DEFAULT_TTL': 300,  
    'NO_CACHE_PATHS': [
        '/admin/',
        '/o/',  
        '/monitoring/',  
    ],
    'PATH_TTLS': {
        '/api/': 60,  
    }
}

MICROSERVICES = {
    'user-service': {
        'endpoints': [
            'http://user-service:8001',
            'http://user-service-backup:8001'
        ],
        'load_balancing': 'round-robin',
        'routes': [
            {
                'path': r'^/api/users/(.*)$',
                'strip_prefix': True,
                'target_path': '/users/$1',
                'methods': ['GET', 'POST', 'PUT', 'DELETE'],
                'auth_required': True,
                'rate_limit': 100
            }
        ]
    },
    'product-service': {
        'endpoints': [
            'http://product-service:8002',
            'http://product-service-backup:8002'
        ],
        'load_balancing': 'random',
        'routes': [
            {
                'path': r'^/api/products/(.*)$',
                'strip_prefix': True,
                'target_path': '/products/$1',
                'methods': ['GET', 'POST', 'PUT', 'DELETE'],
                'auth_required': True
            }
        ]
    },
    'public-service': {
        'endpoints': [
            'http://public-service:8003'
        ],
        'load_balancing': 'random',
        'routes': [
            {
                'path': r'^/public/(.*)$',
                'strip_prefix': False,
                'methods': ['GET'],
                'auth_required': False
            }
        ]
    }
}

SERVICE_REQUEST_TIMEOUT = 30
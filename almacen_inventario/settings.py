# 📁 almacen_inventario/settings.py

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables locales desde .env si el archivo existe.
# Las variables definidas en el sistema conservan prioridad.
load_dotenv(BASE_DIR / '.env')

# SECURITY
SECRET_KEY = 'django-insecure-@&$h&7^3n(zm*2$6%x!p9q$^&*()_+{}:L<>?'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# RABBITMQ
RABBITMQ = {
    'HOST': os.getenv('RABBITMQ_HOST', 'localhost'),
    'PORT': int(os.getenv('RABBITMQ_PORT', '5672')),
    'USER': os.getenv('RABBITMQ_USER', 'guest'),
    'PASSWORD': os.getenv('RABBITMQ_PASSWORD', 'guest'),
    'VIRTUAL_HOST': os.getenv('RABBITMQ_VIRTUAL_HOST', '/'),
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders',
    
    'dominio',
    'aplicacion',
    'presentacion',
    'infraestructura',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'almacen_inventario.urls'

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

WSGI_APPLICATION = 'almacen_inventario.wsgi.application'

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

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'rabbitmq': {
            'format': '{asctime} {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'rabbitmq_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'rabbitmq',
        },
    },
    'loggers': {
        'infraestructura.rabbitmq.inventario_consumer': {
            'handlers': ['rabbitmq_console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

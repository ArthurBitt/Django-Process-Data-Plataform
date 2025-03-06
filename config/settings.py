from decouple import config, Csv
from datetime import timedelta
from pathlib import Path
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = config("DEBUG", cast=bool, default=False)
SECRET_KEY = config('SECRET_KEY')

USE_TZ = True
USE_I18N = True
STATIC_URL = 'static/'
LANGUAGE_CODE = "pt-br"
AUTH_USER_MODEL = "users.User"
TIME_ZONE = 'America/Sao_Paulo'
DATA_UPLOAD_MAX_MEMORY_SIZE = None
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default=[])
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", cast=bool, default=True)

# CELERY CONFIGURATION
CELERY_BROKER_URL = config("REDIS_URL")
CELERY_RESULT_BACKEND = config("REDIS_URL")

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Sao_Paulo"

CELERY_TASK_QUEUES = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'queue_request_api_client': {
        'exchange': 'queue_send_mail_report',
        'routing_key': 'queue_send_mail_report',
    },

    'queue_validate_worksheet_status': {
        'exchange': 'queue_validate_worksheet_status',
        'routing_key': 'queue_validate_worksheet_status',
    },
}

CELERY_TASK_ROUTES = {
    "apps.core.tasks.task_validate_worksheet_status": {
        "queue": "queue_validate_worksheet_status"
    },

    "apps.mail.tasks.task_send_mail_report": {
        "queue": "queue_send_mail_report"
    },
}


LOCAL_APPS = [
    'apps.automation', # app principal
    'apps.worksheets', # app para lidar com planilhas
    'apps.utils', # utilidades - funções auxiliares
    'apps.users',  # app de usuários
    'apps.core',  # core da aplicação
    'apps.mail' # app de envio de e-mails
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_APPS = [
    'rest_framework_simplejwt',  # auth jwt
    'django_celery_results',  # resultados do celery
    'django_celery_beat',  # agendamento de tarefas
    'rest_framework', # api rest
    'drf_api_logger',  # log de api
    'corsheaders', # cors
]

INSTALLED_APPS = LOCAL_APPS + DJANGO_APPS + THIRD_APPS

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'config.wsgi.application'

if not DEBUG:
    DATABASES = {
        "default": dj_database_url.parse(config("DATABASE_URL")),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        "Auth Token eg [Bearer (JWT) ]": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    }
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# Mail
ENDPOINT_MAIL = config("ENDPOINT_SQAD_MAIL")
ID_TEMPLATE_COMPLETED_WORKSHEET = config("ID_TEMPLATE_COMPLETED_WORKSHEET")
MAIL_TOKEN = config("SQAD_MAIL_TOKEN")
EMAIL_TO = config("EMAIL_TO", cast=Csv(), default=[])

# Business rule settings
SLEEPING_PARAMS = config("SLEEPING_PARAMS", cast=Csv(), default=[])
LIMIT_ROBOT = config("LIMIT_ROBOT")
DIRECTORY = config("DIRECTORY")

# Logs
DRF_API_LOGGER_DATABASE = True
DRF_API_LOGGER_SIGNAL = True
DRF_API_LOGGER_TIMEDELTA = -180

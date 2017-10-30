"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DJANGO SETTINGS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


# CONFIG BASED ON HOST

import socket
import ipgetter
host = socket.gethostname()

if host.startswith('test'):
    DEBUG = True #False
    hostIP = ipgetter.myip()
    ALLOWED_HOSTS = [hostIP]
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': 'localhost',
            'PORT': '',
            'NAME': 'erabg',
            'USER': 'testor',
            'PASSWORD': '123qwe',
        }
    }
    
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'asgi_redis.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('localhost', 6379)],
            },
            'ROUTING': 'app_proj.routing.channel_routing',
        }
    }
    
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    
else:       # running on dev machine
    DEBUG = True
    ALLOWED_HOSTS = []
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': 'localhost',
            'PORT': '',
            'NAME': 'erabg',
            'USER': 'postgres',
            'PASSWORD': '123qwe',
        }
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'asgiref.inmemory.ChannelLayer',
            'ROUTING': 'app_proj.routing.channel_routing',
        },
    }



# SERVER CONFIG

ROOT_URLCONF = 'app_proj.urls'

WSGI_APPLICATION = 'app_proj.wsgi.application'

SECRET_KEY = 'j)bo5=v)jlsfpkbrl!(pq8dg-ljoj%r!8mz@twuhe3g_sqlxyo'



# APP CONFIG

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "app_proj/static/")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',         # needed by allauth
    'channels',
    'postman',
    'common',
    'kingdoms',
    'members',                      # before allauth to override templates
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'central',
    'campaign',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'members.middleware.RequestMiddleware',     # set IP during log in
]

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# LOGGING: CRITICAL, ERROR, WARNING, INFO and DEBUG

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    
    'formatters': {
        'simple': {	
            '()': 'common.utility.SimpleFmt'
        },
        'complete': {	
            '()': 'common.utility.CompleteFmt'
        },
    },
    
    'handlers': {
        'console': {
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console_error': {
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'complete'
        },
        'logfile': {
            'class': 'logging.FileHandler',
            'filename': 'logfile.log',
            'formatter': 'complete'
        }
    },
    
    'loggers': {
        'progress': {
            'handlers': ['console'],
            'level': 'DEBUG',
         },
        'exception': {
            'handlers': ['console_error', 'logfile'],
            'level': 'WARNING',
        }
    }
}


# AUTH & ALLAUTH

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

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend"
)

SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'        # users can login with username or email
ACCOUNT_EMAIL_REQUIRED = True                           # require each account to be associated with an email
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'                # 'mandatory' | 'optional' 
ACCOUNT_UNIQUE_EMAIL = True                             # one account per email address
ACCOUNT_SESSION_REMEMBER = False                        # remove remember checkbox from login form
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""                       # override allauth bullshit


# E-MAIL SERVER
# use google mail server while number of emails sent is low
# bullshit security requires that every machine be white listed

EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'zetaszaur@gmail.com'
EMAIL_HOST_PASSWORD = 'zetas345'
EMAIL_USE_TLS = True

# necessary for allauth emails
DEFAULT_FROM_EMAIL = "Era Board Games <no_reply@mg.erabgonline.com>"


# OTHERS

GEOIP_PATH = os.path.join(BASE_DIR, 'members/static/data_sets')






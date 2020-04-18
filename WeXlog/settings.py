"""
Django settings for WeXlog project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
# from __future__ import absolute_import, unicode_literals

import os

# from distutils.sysconfig import get_python_lib
# os.environ["PATH"] += os.pathsep + get_python_lib() + '\\osgeo'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hx*but#(z9!jwy1b2o%sjv3d=k)1h1n^qu%xkwzwb8$h5o4dzf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]',  '107.191.57.249', 'app.mywexlog.dev',]


# Application definition

INSTALLED_APPS = [
    #these must be installed first
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    #allauth-applications
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    #internal Applications
    'users.apps.UsersConfig',
    'Profile.apps.ProfileConfig',
    'db_flatten.apps.DbFlattenConfig',
    'locations.apps.LocationsConfig',
    'enterprises.apps.EnterprisesConfig',
    'project.apps.ProjectConfig',
    'booklist.apps.BooklistConfig',
    'talenttrack.apps.TalenttrackConfig',
    'intmessages.apps.IntmessagesConfig',
    'trustpassport.apps.TrustpassportConfig',
    'marketplace.apps.MarketplaceConfig',
    'payments.apps.PaymentsConfig',
    'public.apps.PublicConfig',
    'invitations.apps.InvitationsConfig',
    'nestedsettree.apps.NestedsettreeConfig',
    'feedback.apps.FeedbackConfig',
    ##Django internal applications
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    #'django.contrib.gis',
    #3rd Party Applications
    'django_countries',
    'crispy_forms',
    'django.contrib.postgres',
    'django_extensions',
    'django_messages',
    'utils',
    'phonenumber_field',
    'leaflet',
    'django_select2',
    'pinax.referrals',
    'pinax.notifications',
    'treebeard',
    'channels',
#    'M2Crypto',
    'paypal.standard.ipn',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
            #3rd party MIDDLEWARE
    'django_referrer_policy.middleware.ReferrerPolicyMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'WeXlog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
#            'loaders': [
#            ('django.template.loaders.cached.Loader', [
#                'django.template.loaders.filesystem.Loader',
#                'django.template.loaders.app_directories.Loader',
#            ]),
#        ],
        },
    },
]

#all-Auth Settings
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True

ACCOUNT_FORMS = {
    'signup': 'users.forms.CustomSignupForm',
}

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 3
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 360
#ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
#ACCOUNT_USER_MODEL_USERNAME_FIELD = 'synonym'
#ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_ADAPTER = 'users.adapter.AccountAdapter'
ACCOUNT_LOGOUT_REDIRECT_URL = '/public/home/'
#ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL =

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]


WSGI_APPLICATION = 'WeXlog.wsgi.application'

ASGI_APPLICATION = 'WeXlog.routing.application'
'''
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
'''
## Web Security Headers
    ##To test use www.securityheaders.com
    ##X-XSS-Protection
SECURE_BROWSER_XSS_FILTER = True
    ##Strict Transport Security (Site must be HTTPS, HTTP rejected)
#SECURE_HSTS_SECONDS = 1800
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True
    ##X-Content-Type-Options
SECURE_CONTENT_TYPE_NOSNIFF = True
    ## X-Frame-Options (DENY, WHITELIST)
X_FRAME_OPTIONS = 'DENY'
    ##django-referrer-policy (3rd party app)
REFERRER_POLICY='same-origin'
    ## Content-Security-policy (3rd party app)
CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", 'SameSite', 'maxcdn.bootstrapcdn.com', 'code.jquery.com',
'cdnjs.cloudflare.com', 'youtube.com', 'fonts.googleapis.com', 'maps.googleapis.com', 'use.typekit.net',
'netdna.bootstrapcdn.com', 'w3.org', '127.0.0.1', '107.191.57.249', 'app.mywexlog.dev', 'kit.fontawesome.com', )

CSP_SCRIPT_SRC = None
CSP_IMG_SRC = ("'self'", '127.0.0.1', '107.191.57.249', 'app.mywexlog.dev')
CSP_OBJECT_SRC = None
CSP_MEDIA_SRC = None
CSP_FRAME_SRC = None
CSP_FONT_SRC = ("'self'", 'fonts.googleapis.com', '*', 'w3.org', '127.0.0.1', '107.191.57.249', 'app.mywexlog.dev')
CSP_CONNECT_SRC = None
CSP_STYLE_SRC = ("'self'", 'maxcdn.bootstrapcdn.com', 'code.jquery.com', 'app.mywexlog.dev',
'cdnjs.cloudflare.com', 'w3.org', '127.0.0.1', '107.191.57.249', 'fonts.googleapis.com', "'unsafe-inline'")
CSP_BASE_URI = None
CSP_CHILD_SRC = None
CSP_FRAME_ANCESTORS = None
CSP_FORM_ACTION = None
CSP_SANDBOX = None
CSP_REPORT_URI = None
CSP_MANIFEST_SRC = None
CSP_WORKER_SRC = None
CSP_PLUGIN_TYPES = None
CSP_REQUIRE_SRI_FOR = None
CSP_UPGRADE_INSECURE_REQUESTS = False
CSP_BLOCK_ALL_MIXED_CONTENT = False
CSP_INCLUDE_NONCE_IN = None
CSP_REPORT_ONLY = False
#CSP_EXCLUDE_URL_PREFIXES = ()
    ##cookie flags
#CSRF_COOKIE_SECURE = True
#CSRF_USE_SESSIONS = True
#CSRF_COOKIE_HTTPONLY = True
#SESSION_COOKIE_SECURE = True
#SESSION_COOKIE_SAMESITE = 'Strict'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        #'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'Wexlog_3',
        'USER': 'postgres',
		'PASSWORD': 'rdf8tm1234', #MA
        #'PASSWORD': 'dJpfss41678', #JK
        'HOST': 'localhost',
        #'HOST': 'dbhost',
        'PORT': '5432'
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


#Authorisation settings
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/Profile/'
LOGOUT_REDIRECT_URL = 'http://mywexlog.dev/public/index/'


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'prod_static')

MEDIA_URL = '/library/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'filelibrary')

#Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# GDAL_LIBRARY_PATH = r'C:/OSGeo4W64/bin/gdal111'

#  os.environ["PATH"] += os.pathsep + BASE_DIR + '\\venv\\Lib\\site-packages\\osgeo'

#POPUP_TEMPLATE_NAME_CREATE = 'popup/create.html'
#POPUP_TEMPLATE_NAME_UPDATE = 'popup/update.html'

#FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

#Django Messages settings
DJANGO_MESSAGES_NOTIFY = False

# PayPal settings
PAYPAL_RECEIVER_EMAIL = "sb-wynfk1244760@business.example.com"
PAYPAL_TEST = True              # set to False for production

# Follow instructions to create new certs for server from https://re.readthedocs.io/es/stable/standard/encrypted_buttons.html to create certs
PAYPAL_PRIVATE_CERT = 'paypal/cert/paypal_private.pem'  #'/path/to/paypal_private.pem'  $ openssl genrsa -out paypal_private.pem 1024
PAYPAL_PUBLIC_CERT = 'paypal/cert/paypal_public.pem'  # '/path/to/paypal_public.pem'  $ openssl req -new -key paypal_private.pem -x509 -days 365 -out paypal_public.pem
PAYPAL_CERT = 'paypal/cert/paypal_cert_pem_1.txt'  # https://www.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert or https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert 'paypal/cert/paypal_cert_pen.txt'
PAYPAL_CERT_ID = 'J7C4RR9N34PZJ'

# Accounts department email_id
ACCOUNTS_EMAIL = "machterberg@tkgm.co.za"


# Celery Settings
CELERY_SYSTEM_EMAIL = 'do_not_reply@mywexlog.com'

## Broker settings.
CELERY_BROKER_URL = 'redis://localhost:6379/0'      # 'amqp://guest:guest@localhost:5672//' for RabbitMQ
CELERY_BACKEND = '#'
#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['application/json']
## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # 'db+sqlite:///results.sqlite'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Australia/Sydney'

# List of modules to import when the Celery worker starts.
CELERY_IMPORTS = ('payments.tasks',)

CELERY_TASK_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}

if DEBUG == True:
    #email settings
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Email settings for Celery
    EMAIL_HOST = ''
    EMAIL_PORT = 465
    EMAIL_HOST_USER = 'do_not_reply@mywexlog.com'
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = True
    """
    # SendGrid mail Settings
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'sendgrid email'
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    """

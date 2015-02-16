"""
Django settings for VToy project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import socket

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


if socket.gethostname() == 'iZ23otdlkscZ':
    RunInCloud = True
else:
    RunInCloud = False
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a$n55-+h5rox$5*c&$1c*vfb!w0-tb)%*at(!u0r10)g@m&sw9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
     'django.contrib.admin',
     'django.contrib.auth',
     'django.contrib.contenttypes',
     'django.contrib.sessions',
     'django.contrib.messages',
     'django.contrib.staticfiles',
     'chat',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'VToy.urls'

WSGI_APPLICATION = 'VToy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
if RunInCloud:
   DATABASES = {
        'default': {
            # 'ENGINE': 'django.db.backends.sqlite3',
            # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'vtoy',
            'USER': 'vtoy',
            'PASSWORD': 'vtoyvtoy',
            'HOST': '127.0.0.1',
            'PORT': '3306'
        }
    }
else:
    DATABASES = {
        'default': {
            # 'ENGINE': 'django.db.backends.sqlite3',
            # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'vtoy',
            'USER': 'root',
            'PASSWORD': 'vtoyvtoy',
            'HOST': '121.40.99.4',
            'PORT': '3306'
        }
    }


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIR = os.path.join(BASE_DIR, 'static/templates')
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

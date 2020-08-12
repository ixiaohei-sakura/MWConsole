import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, 'log')
if not os.path.isdir(LOG_PATH):
    os.mkdir(LOG_PATH)

def read_config() -> dict:
    try:
        f = open(os.path.join("config", "config.json"), 'r')
    except:
        pass
    else:
        JSON = json.loads(f.read())
        return JSON

def _print(data):
    sys.stdout.write(data)
    sys.stdout.write('\r\n')
    sys.stdout.flush()

class MwebLogger():
    def __init__(self: classmethod, level: int, data: str, name='MwebConsole'):
        self.name = name
        self.level = level
        self.data = data
        self.logger()

    def logger(self:classmethod):
        if self.level == 0:
            _print(self.data)
        elif self.level == 1:
            _print(self.data)
        elif self.level == 2:
            _print(self.data)

SECRET_KEY = read_config()['SECRET_KEY']
ALLOWED_HOSTS = read_config()['ALLOWED_HOSTS']
ROOT_URLCONF = read_config()['ROOT_URLCONF']
WSGI_APPLICATION = read_config()['WSGI_APPLICATION']
LANGUAGE_CODE = read_config()['LANGUAGE_CODE']
TIME_ZONE = read_config()['TIME_ZONE']
STATIC_URL = read_config()['STATIC_URL']
USE_I18N = read_config()['USE_I18N']
USE_L10N = read_config()['USE_L10N']
USE_TZ = read_config()['USE_TZ']
DEBUG = read_config()['DEBUG']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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
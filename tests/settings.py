SECRET_KEY = 'i0_+-t@@wul&q)30+4y)8-19s)31@%cv8$q(c@8q1g#h$6wn-='

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

## Thumbor ##
THUMBOR_SERVER = 'http://ro.thumbor-server'
THUMBOR_WRITABLE_SERVER = 'http://rw.thumbor-server'
#THUMBOR_MEDIA_URL = 'http://localhost:8000/media'
THUMBOR_SECURITY_KEY = 'MY_SECURE_KEY'

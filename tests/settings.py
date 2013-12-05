SECRET_KEY = 'i0_+-t@@wul&q)30+4y)8-19s)31@%cv8$q(c@8q1g#h$6wn-='

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

MEDIA_URL = 'http://media.my_project.com/'
MEDIA_ROOT = '/media'

## Thumbor ##
THUMBOR_SERVER = 'http://ro.thumbor-server'
THUMBOR_SECURITY_KEY = 'my-secure-key'
THUMBOR_RW_SERVER = 'http://rw.thumbor-server'
THUMBOR_SECURITY_KEY = 'MY_SECURE_KEY'

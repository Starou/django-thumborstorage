=====================
django-thumborstorage
=====================

.. image:: https://coveralls.io/repos/Starou/django-thumborstorage/badge.png?branch=master
:target: https://coveralls.io/r/Starou/django-thumborstorage?branch=master 

A Django custom storage for Thumbor backend.

**Important:** This package is still under development and should be used with care.
Contributions are welcome!

This app provide 2 classes ``ThumborStorage`` and ``ThumborMigrationStorage``. The last one
is a storage you can use for ``Imagefield`` initialy using a ``FileSystemStorage`` you want
to migrate to Thumbor without batch-moving all of them. That way, Django continues to serve
them from the file system until you change the image on that field.


Install
=======

::

    pip install django-thumborstorage


Dependencies
''''''''''''

* Python 2.6 or 2.7
* Django-1.5.x
* Requests_

Recommended:

* Django-thumbor_ (to manage thumbnails).
* Thumbor_


Usage
=====

settings.py
'''''''''''

Add ``django-thumborstorage`` in your ``INSTALLED_APPS``.

And set the following::

    THUMBOR_SERVER = 'http://localhost:8888'
    THUMBOR_WRITABLE_SERVER = THUMBOR_SERVER
    THUMBOR_SECURITY_KEY = 'MY_SECURE_KEY'

``THUMBOR_WRITABLE_SERVER`` exists because in some configurations you write on one server and read on another.


models.py
'''''''''

Just set the ``storage`` parameter in the ImageField you want to manage with Thumbor::

    from django_thumborstorage.storages import ThumborStorage

    class Stuff(models.Model):
        def upload_path(instance, filename):
            return 'stuffs/%s' % filename
        photo = models.ImageField(upload_to=upload_path,
                                  storage=ThumborStorage(),
                                  height_field='photo_height',
                                  width_field='photo_width')
        photo_height = models.IntegerField(blank=True, null=True)
        photo_width = models.IntegerField(blank=True, null=True)


TODO
====

* PUT, DELETE

.. _Requests: http://www.python-requests.org/en/latest/
.. _Thumbor: https://github.com/globocom/thumbor
.. _Django-thumbor: https://django-thumbor.readthedocs.org/en/latest/

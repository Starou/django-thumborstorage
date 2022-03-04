=====================
django-thumborstorage
=====================

.. image:: https://coveralls.io/repos/github/Starou/django-thumborstorage/badge.svg?branch=master
  :target: https://coveralls.io/github/Starou/django-thumborstorage?branch=master

.. image:: https://img.shields.io/pypi/v/django-thumborstorage.svg
  :target: https://pypi.python.org/pypi/django-thumborstorage

A Django custom storage for Thumbor.

Provides 2 custom storages classes: ``ThumborStorage`` and ``ThumborMigrationStorage``.

Use ``ThumborMigrationStorage`` on an ``Imagefield`` that started with a classic
``FileSystemStorage`` you want to upgrade to Thumbor without migrating your old
media. That way, Django continues to serve them from the file system until the
image is changed.

Install
=======

::

    pip install django-thumborstorage

Dependencies
''''''''''''

* Python 3.6+
* Django 2.1 to 3.2
* Requests_
* Libthumbor_

Recommended:

* Django-thumbor_ (to manage thumbnails).
* Thumbor_

Usage
=====

settings.py
'''''''''''

Add ``django_thumborstorage`` in ``INSTALLED_APPS``.

And set the following with your values:

.. code-block:: python

    THUMBOR_SERVER = 'https://my.thumbor.server.com:8888'
    THUMBOR_SECURITY_KEY = 'MY_SECURE_KEY'
    # This may be a different host than THUMBOR_SERVER
    # only reachable by your Django server.
    THUMBOR_RW_SERVER = 'https://my.rw.thumbor.server.local:8888'

models.py
'''''''''

Just set the ``storage`` parameter in the ImageField you want to manage with Thumbor:

.. code-block:: python

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

In the code
'''''''''''

You can get the Thumbor ``uuid`` from the ``<ImageField>`` instance using:

.. code-block:: python

    my_stuff.photo.storage.key(my_stuff.photo.name)

This is useful to ``generate_url()`` with Django-thumbor_ when original files are stored on Thumbor. Thus,
you can pass the key as url parameter.

CHANGELOG
=========

2.0.0
'''''

* Add support for Django 3.2.

Possible breaking change
------------------------

The leading ``/`` in the path of the file stored in the database has been removed
due to a breaking change introduced un Django 3.2.11.

https://docs.djangoproject.com/en/4.0/releases/3.2.11/#cve-2021-45452-potential-directory-traversal-via-storage-save

That release handle seamlessly both pre-2.0.0 style (*/image/...*) and
post-2.0.0 style paths (*image/...*) so there is not need to migrate your database
to replace */image/...* with *image/...*.


1.13.0
''''''

* Drop support for Django < 2.1 and Python 2.7, 3.4 and 3.5
* Use GitHub actions for CI instead of Travis.


1.11.0
''''''

* Drop support for Django < 1.11 and Python 3.4.
* Remove ``mock`` from dependencies.


0.92.2
''''''

* Fix ``readonly_to_rw_url()`` to manage suffix in the urls.

0.92.1
''''''

* Handle status code of the Thumbor server response when posting an image.

0.92.0
''''''

* Added experimental Python 3.4 support (Thanks to *Charlie 123*.)
* Fixed broken support for Django < 1.7 (Thanks to *Rizziepit*.)
* Added unicode support in file names (Thanks to *Rizziepit*.)

0.91.6
''''''

* Add ``storages.readonly_to_rw_url()``, a function to convert a read-only thumbor url in a rw url.

0.91.5
''''''

* Use THUMBOR_SERVER to generate the original file url.

Backward imcompatibilities
--------------------------

* ``THUMBOR_SERVER`` and ``THUMBOR_SECURITY_KEY`` are required in settings.

0.91.4
''''''

* Add ``ThumborStorage.key(name)`` to retrieve the Thumbor uuid from the name.

0.91.3
''''''

Backward imcompatibilities
--------------------------

* ``THUMBOR_WRITABLE_SERVER`` setting is replaced by ``THUMBOR_RW_SERVER`` since it is now used to retrieve the
  original file.

TODO
====

* PUT

.. _Requests: http://www.python-requests.org/en/latest/
.. _Thumbor: https://github.com/globocom/thumbor
.. _Libthumbor: https://github.com/heynemann/libthumbor
.. _Django-thumbor: https://django-thumbor.readthedocs.org/en/latest/

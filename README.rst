=====================
django-thumborstorage
=====================

.. image:: https://coveralls.io/repos/Starou/django-thumborstorage/badge.png?branch=master
  :target: https://coveralls.io/r/Starou/django-thumborstorage?branch=master

.. image:: https://pypip.in/v/django-thumborstorage/badge.png
  :target: https://pypi.python.org/pypi/django-thumborstorage

.. image:: https://travis-ci.org/Starou/django-thumborstorage.svg
    :target: https://travis-ci.org/Starou/django-thumborstorage
    :alt: Travis C.I.

A Django custom storage for Thumbor backend.

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

* Python 2.7
* Python 3.4
* Django-1.5+
* Requests_

Recommended:

* Django-thumbor_ (to manage thumbnails).
* Thumbor_


Usage
=====

settings.py
'''''''''''

Add ``django_thumborstorage`` in your ``INSTALLED_APPS``.

And set the following:

.. code-block:: python

    THUMBOR_SERVER = 'http://localhost:8888'
    THUMBOR_SECURITY_KEY = 'MY_SECURE_KEY'
    # This may be a different host than THUMBOR_SERVER
    # only reachable by your Django server.
    THUMBOR_RW_SERVER = 'http://localhost:8888'



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
0.91.9
''''''

* Add Python 3.4 support
* Removed Dependency on libthumbor as it is not Python 3.4 compatible


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

=====================
django-thumborstorage
=====================

A Django custom storage for Thumbor backend.

**Important:** Still in development.


This app provide 2 classes ``ThumborStorage`` and ``ThumborMigrationStorage``. The last one
is a storage you can use for ``Imagefield`` initialy using a ``FileSystemStorage`` you want
to migrate to Thumbor without batch-moving all of them. That way, Django continues to serve
them from the file system until you change the image on that field.


Install
=======

::

    pip install django-thumborstorage


TODO
====

* PUT, DELETE

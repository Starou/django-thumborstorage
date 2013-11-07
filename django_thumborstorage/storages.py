import os
import requests
from StringIO import StringIO
from django.conf import settings
from django.core.files.images import ImageFile
from django.core.files.storage import Storage, FileSystemStorage
from django.utils.http import urlencode


class ThumborStorageFile(ImageFile):
    def __init__(self, name, mode):
        self.name = name
        self._file = None
        self._location = None
        self._mode = mode

    def write(self, *args, **kwargs):
        content = kwargs.pop("content")
        image_content = content.file.read()
        content.file.seek(0)

        url = "%s/image" % settings.THUMBOR_WRITABLE_SERVER
        headers = {
            "Content-Type": "image/jpeg",
            "Slug": self.name,
        }
        response = requests.post(url, data=image_content, headers=headers)
        self._location = response.headers["location"]
        return super(ThumborStorageFile, self).write(image_content)

    def _get_file(self):
        if self._file is None:
            self._file = StringIO()
            if 'r' in self._mode:
                url = "%s%s" % (settings.THUMBOR_SERVER, self.name)
                response = requests.get(url)
                self._file.write(response.content)
                self._file.seek(0)
        return self._file

    def _set_file(self, value):
        self._file = value

    file = property(_get_file, _set_file)
    

class ThumborStorage(Storage):
    """Thumbor Simple Storage Service"""

    def __init__(self, options=None):
        pass

    def _open(self, name, mode='rb'):
        f = ThumborStorageFile(name, mode)
        return f

    def _save(self, name, content):
        name = self._normalize_name(name)
        f = ThumborStorageFile(name, mode="w")
        f.write(content=content)
        return f._location

    def _normalize_name(self, name):
        return name

    def delete(self, name):
        # https://docs.djangoproject.com/en/1.5/ref/files/storage/#django.core.files.storage.Storage.delete
        pass

    def exists(self, name):
        pass
        # https://docs.djangoproject.com/en/1.5/ref/files/storage/#django.core.files.storage.Storage.exists

    def size(self, name):
        pass
        # https://docs.djangoproject.com/en/1.5/ref/files/storage/#django.core.files.storage.Storage.size

    def url(self, name):
        return "%s%s" % (settings.THUMBOR_SERVER, name)

    #TODO : get_valid_name(name) et get_available_name(name).


class ThumborMigrationStorage(ThumborStorage, FileSystemStorage):
    """A Storage that fallback on the FileSystemStorage.
    
    Useful for a parallel run strategy.

    The use case is :
        1. Your project started with a FileSystemStorage ;
        2. You want to switch to Thumbor to store your images
            without moving all of them at once.
        
    So:
        1. Store the new images on Thumbor ;
        2. continue to serve existing ones from the file system.
    """
    pass

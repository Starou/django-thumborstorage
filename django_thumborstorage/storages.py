import mimetypes
import os
import re

from io import BytesIO
from urllib.parse import quote, unquote

import requests

from libthumbor import CryptoURL
from requests.packages.urllib3.exceptions import LocationParseError
from django.conf import settings
from django.core.files.images import ImageFile
from django.core.files.storage import Storage, FileSystemStorage
from django.utils.deconstruct import deconstructible
from . import exceptions


# Match 'key', 'key/filename.ext' and 'key.ext'.
# Backward-compatibility with the breaking change in Django 3.2.11.
# We can have pre-Django-3.2.11 path in the database that still start with '/'.
# https://github.com/django/django/commit/6d343d01c57eb03ca1c6826318b652709e58a76e
THUMBOR_PATH_PATTERN = r"^/?image/(?P<key>\w{32})(?:(/|\.).*){0,1}$"


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

        url = f"{settings.THUMBOR_RW_SERVER}/image"
        headers = {
            "Content-Type": mimetypes.guess_type(self.name)[0] or "image/jpeg",
            "Slug": quote(self.name.encode('utf-8'), ':/?#[]@!$&\'()*+,;='),
        }
        response = requests.post(url, data=image_content, headers=headers)
        if response.status_code != 201:
            raise exceptions.ThumborPostException(response)
        self._location = unquote(response.headers["location"])
        try:
            self._location = self._location.decode('utf-8')
        except AttributeError:
            pass
        return super().write(image_content)

    def delete(self):
        url = f"{settings.THUMBOR_RW_SERVER}{self.get_location()}"
        response = requests.delete(url)
        if response.status_code == 405:
            raise exceptions.MethodNotAllowedException
        if response.status_code == 404:
            raise exceptions.NotFoundException
        if response.status_code == 204:
            return

    def _get_file(self):
        if self._file is None or self._file.closed:
            self._file = BytesIO()
            if 'r' in self._mode:
                url = f"{settings.THUMBOR_RW_SERVER}{self.get_location()}"
                response = requests.get(url)
                self._file.write(response.content)
                self._file.seek(0)
        return self._file

    def _set_file(self, value):
        self._file = value

    file = property(_get_file, _set_file)

    def get_location(self):
        """ Django 3.2.11 introduced a backward-incompatible change.

        See https://github.com/django/django/commit/6d343d01c57eb03ca1c6826318b652709e58a76e
        This function manage both pre and post Django 3.2.11 name in the database (with
        and without a '/' at the start of the string.
        """
        location = self.name
        if not location[0] == '/':
            location = '/' + location
        return location


    @property
    def size(self):
        self.seek(0, os.SEEK_END)
        return self.tell()

    def close(self):
        super().close()
        self._file = None


@deconstructible
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
        # The '/' at the beginning of the 'name' save in the db is no more allowed
        # since Django 3.2.11.
        # https://github.com/django/django/commit/6d343d01c57eb03ca1c6826318b652709e58a76e
        return f._location[1:]

    def _normalize_name(self, name):
        return name

    def delete(self, name):
        f = self.open(name)
        f.delete()

    def exists(self, name):
        # name is the location returned by Thumbor when posted > may exists.
        if re.match(THUMBOR_PATH_PATTERN, name):
            return thumbor_original_exists(thumbor_original_image_url(name))
        # name as defined in 'upload_to' > new image.
        return False

    def size(self, name):
        f = self.open(name)
        return f.size

    def url(self, name):
        return thumbor_image_url(self.key(name))

    def key(self, name):
        return re.match(THUMBOR_PATH_PATTERN, name).groupdict()['key']

    def get_available_name(self, name, max_length=None):
        # There is no way to know if the image exists on Thumbor.
        # When posting a new original image, Thumbor generate a ramdom unique id as key.
        # http://en.wikipedia.org/wiki/Universally_unique_identifier
        # https://github.com/globocom/thumbor/blob/ae9a150e8a2b771dd49b4137186e9fdfbea09733/thumbor/handlers/images.py#L51
        return name

    # TODO : get_valid_name(name)


@deconstructible
class ThumborMigrationStorage(ThumborStorage, FileSystemStorage):
    """A Storage that fallback on the FileSystemStorage when retrieving the image.

    Useful for a parallel run migration strategy.

    The use case is :
        1. Your project started with a FileSystemStorage ;
        2. You want to switch to Thumbor to store your images
            without moving all of them at once.

    So:
        1. Store the new images on Thumbor ;
        2. continue to serve existing ones from the file system.
    """

    def __init__(self, **kwargs):
        options = kwargs.get("options", None)
        location = kwargs.get("location", None)
        base_url = kwargs.get("base_url", None)
        # TODO if django >= 1.6: file_permissions_mode
        ThumborStorage.__init__(self, options)
        FileSystemStorage.__init__(self, location=location, base_url=base_url)

    def _open(self, name, mode='rb'):
        if self.is_thumbor(name):
            return ThumborStorage._open(self, name, mode)
        return FileSystemStorage._open(self, name, mode)

    def delete(self, name):
        if self.is_thumbor(name):
            return ThumborStorage.delete(self, name)
        return FileSystemStorage.delete(self, name)

    def exists(self, name):
        if self.is_thumbor(name):
            return ThumborStorage.exists(self, name)
        return FileSystemStorage.exists(self, name)

    def url(self, name):
        if self.is_thumbor(name):
            return ThumborStorage.url(self, name)
        return FileSystemStorage.url(self, name)

    def key(self, name):
        if self.is_thumbor(name):
            return ThumborStorage.key(self, name)
        raise NotImplementedError

    def path(self, name):
        if self.is_thumbor(name):
            return ThumborStorage.path(self, name)
        return FileSystemStorage.path(self, name)

    def is_thumbor(self, name):
        return re.match(THUMBOR_PATH_PATTERN, name)


def thumbor_original_exists(url):
    # May be cool to be able to check if the image exists on Thumbor server
    # *without* having to retrieve it.
    try:
        response = requests.get(url)
    # Happens when trying to get an image when the name in db
    # is in a FileSystemStorage form (without the leading slash).
    except LocationParseError:
        return False
    if response.status_code == 200:
        return True
    return False


# These functions because some methods in ThumborStorage may be called with
# self being a ThumborMigrationStorage instance and result in infinite loop.
# These methods proxiing to these functions.

def thumbor_image_url(key):
    crypto = CryptoURL(key=settings.THUMBOR_SECURITY_KEY)
    return f"{settings.THUMBOR_SERVER}{crypto.generate(image_url=key)}"


def thumbor_original_image_url(name):
    """ Django 3.2.11 introduced a backward-incompatible change.

    See https://github.com/django/django/commit/6d343d01c57eb03ca1c6826318b652709e58a76e
    This function manage both pre and post Django 3.2.11 name in the database (with
    and without a '/' at the start of the string.
    """
    if not name[0] == '/':
        name = '/' + name
    return f"{settings.THUMBOR_RW_SERVER}{name}"


# Utils

def readonly_to_rw_url(readonly_url):
    matches = re.match(r"^%s/(?P<secu>[\w\-=]{28})/(?P<key>\w{32})(?P<extra>(?:.*))$" %
                       re.escape(settings.THUMBOR_SERVER), readonly_url).groupdict()
    name = f"/image/{matches['key']}{matches['extra']}"
    return thumbor_original_image_url(name)

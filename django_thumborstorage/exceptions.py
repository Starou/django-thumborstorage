class DjangoThumborStorageException(BaseException):
    pass


class NotFoundException(DjangoThumborStorageException):
    """ 404 - Not Found """


class MethodNotAllowedException(DjangoThumborStorageException):
    """ 405 - Method Not Allowed """


class ThumborPostException(DjangoThumborStorageException):
    _error = None

    def __init__(self, response):
        self._error = "%d - %s" % (response.status_code, response.reason)

    def __repr__(self):
        print(self._error)

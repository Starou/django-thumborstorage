class DjangoThumborStorageException(BaseException):
    pass


class NotFoundException(DjangoThumborStorageException):
    """ 404 - Not Found """


class MethodNotAllowedException(DjangoThumborStorageException):
    """ 405 - Method Not Allowed """

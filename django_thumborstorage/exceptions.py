class DjangoThumborStorageException(BaseException):
    pass


class MethodNotAllowedException(DjangoThumborStorageException):
    """ 405 - Method Not Allowed """

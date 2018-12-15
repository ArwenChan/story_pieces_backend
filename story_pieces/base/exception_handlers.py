from rest_framework.views import exception_handler as default_exception_handler

from .exceptions import BusinessException
from .utils import business_exception_handler



def exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    if isinstance(exc, BusinessException):
        response = business_exception_handler(exc, context)
    else:
        response = default_exception_handler(exc, context)

    return response
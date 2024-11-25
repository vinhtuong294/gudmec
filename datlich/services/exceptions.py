from rest_framework.exceptions import APIException


class NotFoundException(APIException):
    status_code = 404
    default_detail = "Resource not found"
    default_code = "not_found"

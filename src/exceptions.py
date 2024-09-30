from typing import Optional

from fastapi import HTTPException, status


class BaseException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = ""

    def __init__(self, detail: Optional[str] = None):
        if detail is not None:
            self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)



class ErrorBaseAioHttpServiceUnavailable(BaseException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Service unavailable"


class ErrorBaseAioHttpServiceRequestTimeout(BaseException):
    """Исключение для таймаутов."""
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    detail = "Request timed out"


class ErrorBaseAioHttpServiceBadRequest(BaseException):
    """Исключение для ошибок клиента."""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Client error"


class ErrorBaseAioHttpServiceServerError(BaseException):
    """Исключение для ошибок сервера."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Server error"
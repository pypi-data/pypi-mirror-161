import typing as t
from requests import Response


__all__ = [
    'BitpinExceptions',
    'RequestsExceptions',
    'RequestTimeout',
    'InvalidToken',
    'InvalidResponse',
    'StatusCodeError',
    'JSONDecodingError'
]


class BitpinExceptions(Exception):
    def __init__(
            self, func_name: str, message: t.Union[str, t.Type[Exception], Exception], *args, **kwargs
    ):
        """
        Base exception class for Bitpin.

        :param func_name: function name that raise exception
        :type func_name: str

        :param message: message of exception
        :type message: str | Exception

        :param args: args of exception
        :type args: t.Any

        :param kwargs: kwargs of exception
        :type kwargs: t.Any

        :return: None
        :rtype: None
        """

        self.func_name = func_name
        self.message = str(message)
        self.args_ = args
        self.kwargs_ = kwargs
        super().__init__(self.message)

    def __str__(self):
        __str = f'[{self.func_name}] -> {self.message}'

        if self.args_:
            __str += f' | Args: {self.args_}'
        if self.kwargs_:
            __str += f' | Kwargs: {self.kwargs_}'

        return __str


class RequestsExceptions(BitpinExceptions):
    """ Exception class for requests error. """


class RequestTimeout(RequestsExceptions):
    """ Exception class for requests timeout error. """


class InvalidToken(RequestsExceptions):
    """ Exception class for invalid token error. """


class ProcessExceptions(BitpinExceptions):
    """ Exception class for process error. """

    def __init__(self, func_name: str, message: t.Union[str, t.Type[Exception], Exception],
                 response: t.Optional[Response] = None, *args, **kwargs):

        self.func_name = func_name
        self.message = str(message)
        self.args_ = args
        self.kwargs_ = kwargs
        self.response = response

        super().__init__(self.func_name, self.message)

    def __str__(self):
        __str = f'[{self.func_name}] -> {self.message}'

        if self.args_:
            __str += f' | Args: {self.args_}'
        if self.kwargs_:
            __str += f' | Kwargs: {self.kwargs_}'

        return __str


class StatusCodeError(ProcessExceptions):
    """ Exception class for status code error. """


class JSONDecodingError(ProcessExceptions):
    """ Exception class for json decode error. """


class InvalidResponse(ProcessExceptions):
    """ Exception class for invalid response error. """

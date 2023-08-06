from typing import Dict


class GqlError(Exception):
    def __init__(self, body=None, headers: Dict = None, message: str = '', status_code: int = 0, summary: str = ''):
        self.body = body
        self.headers = headers
        self.message = message
        self.status_code = status_code
        self.summary = summary
        self.retryable = status_code >= 500
        super(GqlError, self).__init__()

    def __str__(self) -> str:
        return self.summary


class InvalidSessionError(Exception):
    pass


class InvalidConfigFileError(Exception):
    pass

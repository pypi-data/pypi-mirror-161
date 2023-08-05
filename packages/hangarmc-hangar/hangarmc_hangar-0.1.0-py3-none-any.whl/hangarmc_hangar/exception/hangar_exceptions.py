from typing import Dict


class HangarApiException(Exception):
    def __init__(self, status: int, data: Dict):
        self.status = status
        self.data = data

    def __str__(self):
        if 'message' in self.data:
            return f"{self.status}: {self.data['message'].format(self.data['messageArgs'])}"
        return f"{self.status}: {self.data['error']} at {self.data['path']}"


class HangarDownloadException(Exception):
    def __init__(self, status: int):
        self.status = status

    def __str__(self):
        return f"HTTP {self.status} hit while downloading"


class HangarAuthenticationException(HangarApiException):
    def __init__(self, status: int, data: Dict):
        super().__init__(status, data)

    def __str__(self):
        if self.status == 400:
            return "400: Bad Request"
        elif self.status == 401:
            return "401: API Key missing or invalid"
        elif self.status == 403:
            return "403: Not enough permissions to use this endpoint"
        elif self.status == 404:
            return "404: Not Found"
        return super().__str__()

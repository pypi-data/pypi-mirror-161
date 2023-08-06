
import string

class Response:
    def __init__(self, data: object = None, message: string = None, status: int = None) -> None:
        self.data = data
        self.message = message
        self.status = status
    
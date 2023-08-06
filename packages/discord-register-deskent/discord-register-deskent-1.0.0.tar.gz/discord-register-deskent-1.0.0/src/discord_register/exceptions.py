class RegisterBaseException(BaseException):
    def __init__(self, text: str = ''):
        self.text: str = text

    def __str__(self):
        return self.text


class EmailError(RegisterBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "Email class error"


class CaptchaError(RegisterBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "Email class error"


class DiscordRegistererError(RegisterBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "DiscordRegisterer class error"


class ProxyError(RegisterBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "ProxyError class error"

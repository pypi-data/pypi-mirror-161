class GrabberBaseException(BaseException):
    def __init__(self, text: str = ''):
        self.text: str = text

    def __str__(self):
        return self.text


class CaptchaTimeoutError(GrabberBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "Captcha time is over. Please try later..."


class CaptchaAPIkeyError(GrabberBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "Anticaptcha API key error"


class RequestError(GrabberBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "Request error"


class FingerPrintError(GrabberBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "No fingerprint got error"


class MailReaderError(GrabberBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "MailReader error"

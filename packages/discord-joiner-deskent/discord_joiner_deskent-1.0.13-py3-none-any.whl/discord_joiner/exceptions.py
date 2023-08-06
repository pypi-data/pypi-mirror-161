class JoinerBaseException(Exception):
    def __init__(self, text: str = ''):
        self.text: str = text

    def __str__(self):
        return self.text


class CooldownError(JoinerBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or 'Request cooldown error'


class FingerprintError(JoinerBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or 'Fingerprint error'


class AuthorizationtError(JoinerBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or 'Authorization Error: Invalid token'


class InviteLinkError(JoinerBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or 'Invite link is not valid'


class JoiningError(JoinerBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or 'Joining error'


class ProxyError(JoinerBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or 'Proxy error'


class CaptchaAPIkeyError(JoinerBaseException):
    def __init__(self, text: str = ''):
        self.text: str = text or "Anticaptcha API key error"

class GeneralException(Exception):
    """Главное исключение"""


class UserAlreadeRegistered(GeneralException):
    """
    Ошибка вызываемая при повторной регистрации пользователя с таким же email
    """

    def __init__(self, email: str):
        self.email = email


class IncorrectUserLoginData(GeneralException):
    """
    Вызывается при неправильном вводе данных для входа в аккаунт
    """

    def __init__(self, password: str, login: str):
        self.message = "Incorrect login data"
        self.password = (password,)
        self.login = login


class TokenException(GeneralException):
    """Базовое исключение для токена"""

    detail = "Ошибка токена"


class TokenNotValidException(TokenException):
    """Ошибка вызываемая при валидации токена"""

    detail = "Токен не валдиен"


class TokenSignatureException(TokenException):
    """Ошибка сигнатуры токена"""

    detail = "Ошибка сигнатуры токена"


class TokenExpiredException(TokenException):
    """Ошибка времени жизни токена"""

    detail = "Время жизни токена истекло"


class UnauthenticatedUser(GeneralException):
    """Пользователь не аутентифицирован"""


class RedisException(Exception):
    """Общее исключение для Redis ошибок"""


class RedisConnectionException(RedisException):
    """Ошибка подключения к Redis"""


class RedisTimeoutException(RedisException):
    """Вышло время подключения к Redis"""

class UserAlreadeRegistered(Exception):
    """
    Ошибка вызываемая при повторной регистрации пользователя с таким же email
    """

    def __init__(self, email: str):
        self.email = email


class TokenValidException(Exception):
    ''' Ошибка вызываемая при валидации токена '''
    def __init__(self, error_message: str):
        self.error_message = error_message
class UserAlreadeRegistered(Exception):
    """
    Ошибка вызываемая при повторной регистрации пользователя с таким же email
    """

    def __init__(self, email: str):
        self.email = email

from bcrypt import gensalt, hashpw, checkpw


class HashingPassword:
    def create_hash(self, password: str) -> bytes:
        ''' Создание хэша по паролю '''
        hash = hashpw(password.encode("utf-8"), gensalt())
        
        return hash
    
    def password_verification(self, password: str, hash: bytes) -> bool:
        ''' Проверка соответствия пароля хэшу  '''
        return checkpw(password.encode("utf-8"), hash)
    

hashing_password = HashingPassword()
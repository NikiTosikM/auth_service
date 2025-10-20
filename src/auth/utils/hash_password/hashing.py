from bcrypt import gensalt, hashpw, checkpw


class Hashing:
    def create_hash(self, data: str) -> bytes:
        """Создание хэша"""
        hash = hashpw(data.encode("utf-8"), gensalt())

        return hash

    def hash_verification(self, data: str, hash: bytes) -> bool:
        """Проверка соответствия хэшу"""
        return checkpw(data.encode("utf-8"), hash)


hashing = Hashing()

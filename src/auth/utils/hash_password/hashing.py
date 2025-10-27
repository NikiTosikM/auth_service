from bcrypt import gensalt, hashpw, checkpw
from loguru import logger


class Hashing:
    def create_hash(self, data: str) -> bytes:
        """Создание хэша"""

        hash = hashpw(data.encode("utf-8"), gensalt())

        logger.debug(f"Создан hash для {data}")

        return hash

    def hash_verification(self, data: str, hash: bytes) -> bool:
        """Проверка соответствия хэшу"""
        logger.debug(f"Проверка hash на соответствие {data}")

        return checkpw(data.encode("utf-8"), hash)


hashing = Hashing()

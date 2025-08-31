from datetime import datetime, timezone, timedelta
from uuid import uuid4
import jwt

from enum import Enum
from uuid import UUID
import re

from pydantic import (
    BaseModel, 
    Field, 
    EmailStr, 
    model_validator, 
    ValidationError
)
from fastapi.exceptions import HTTPException
from fastapi import status
from redis.asyncio import Redis

from auth.service import RedisManager

private_key = '''-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCWm1HA0iQ2/BGq
DmFJXocWmm829ZvSrbZMb4eQL+AyHbA/a8Bv1L1wSkwmVYzUQtNZkvz1YDlZW2wL
nWN3w5XbwDNBavB3MOWWqGyWDy5QDYOyHyQ/duaN5sn+ley0V6XBVJQQzkDL3tym
Tx27jpSh9B/9V15hKLF4AEQqznSf8HdU+s+ZFcv8MKRXpVB9niCMMuWVnBQDH1uq
54LXHDshawOjcEYsVGCAC2UYiGYZV4bt/5359rBF4kq/qY+yRZgRM+xfYyIf+aAx
0xDziOQ7pbxkMsaXsVNd8SKc1CtyjR7tmwDGTihy9uNLoDmU/JfzMBSYm9nIiBzE
Oaa+k8fTAgMBAAECggEAPMVCiUAiHc+7nvd7eRv7/XpmavJTJIE0wIX2WQ+Acyh4
oDat6VIZ+K/6JzO5BkNKveeqS6a+rVhO8ibZZo+Urh3RcNGiYy3nTlH6sthAU0wI
unyHZ1ZmdJbOJfzADQsa1rZ2ootfKQRt22usLyy6u9jieZrh+eluJuJQn0c8VvaV
yk+lI+Gaj2bEQhuSfBSazZ0IzlbRPgnAavdNLUuzkr3hUEBrTNa4r2k1EAviY3HA
MR4H2yqx9TN71a4/OcW53q+F+iZ6+IOx3YAST5z8gAEHgos6CLAeFuzPZnrQSPq+
QXRhZDsUUSpjUS+OtHXw1/INy6BQ4J36cSsiujJarQKBgQDNNU00z59TChAJUsva
1wq8JULMRji0UuJPfV7bieiAzLIiqsBxSS3TPzTuGYFBFqyCL+CMziHvEVGgNjaH
WRS1flFh50T6jCTLdOd0lM3I+SALR9Am+TbLHQaflEzQpGY7o7NK39N81WQb9ScW
Mtu55sEyx4HNJaNPH6vc9URzlwKBgQC74kd74ZgjMc20J+3Osln1QGfW8hR8QKoH
JsjFnZdkNSO2xHFlTjzdjZFQ8aZWs+8Xb/Fux/06cmLlTAAodroizkWcccq5vuTm
7RAW3z+TT0kwCH+3zByc2oUalz5hH7iGsPu/A3kXivDiay+ohWm3V3HVFcK9UYs2
j24Plx/lJQKBgEWMvzIa/GDklDLUwQrWv2itKEqbsjRLszBFyZSW1RpyRh3ByZ+b
sdBbJ9FbC5fH24f0OiL+6jlgoU2vkiOlaYNp4KNSAur3/LCIWroEhQqMhPPNzxqm
dI+6srf7R12fmpa0ENxbqA4zNM7U8/5uFlKXhvty6udgzkzO6yzkY+LZAoGBAKcT
juvr7iWF+V32j/PaCEMe1fh/55Wiz1ByveF1xZXX53107T3gOCHw7UOk0H2Tns8h
vfn8oARkietMDWvuQJIJCkAXtOY+ikGMmF0ug9OUkwnC1Qh12w/lBq5hxpgJ5Ebq
hcQT64/y/0jpdkUO9raSbWjG5BkEtZ58J6x3gGZ9AoGBAMgFAkr0fkaclaMAuJNt
dRqXJiQbU9daMznWHtKm5m6JAio3e6P4U/R71nGkXRrdEnVZuKRvPQ0PuAFxbh95
99fXSFp+evaiUH8GZ2IhZsSg30JtUNU2nAAUQcNgWPNg1ADKxseaF9La+XolqhVm
oNd3XL7Ys0RzDD1b67vl7Lhy
-----END PRIVATE KEY-----'''

public_key = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlptRwNIkNvwRqg5hSV6H
FppvNvWb0q22TG+HkC/gMh2wP2vAb9S9cEpMJlWM1ELTWZL89WA5WVtsC51jd8OV
28AzQWrwdzDllqhslg8uUA2Dsh8kP3bmjebJ/pXstFelwVSUEM5Ay97cpk8du46U
ofQf/VdeYSixeABEKs50n/B3VPrPmRXL/DCkV6VQfZ4gjDLllZwUAx9bqueC1xw7
IWsDo3BGLFRggAtlGIhmGVeG7f+d+fawReJKv6mPskWYETPsX2MiH/mgMdMQ84jk
O6W8ZDLGl7FTXfEinNQrco0e7ZsAxk4ocvbjS6A5lPyX8zAUmJvZyIgcxDmmvpPH
0wIDAQAB
-----END PUBLIC KEY-----'''


class UserRole(str, Enum):
    user = "user"
    admin = "admin"

# from auth.schemas import UserResponce
# from core import settings

class UserResponce(BaseModel):
    id: int
    email: EmailStr
    role: UserRole


class JwtManager:
    def __init__(self, client: Redis):
        self._redis_manager = RedisManager(client=client)
        self._private_key: str = private_key #settings.auth.private_key.read_text()
        self._public_key: str = public_key #settings.auth.private_key.read_text()
        self._access_token_lifetime: int = 10 #settings.auth.access_token_lifetime_minutes
        self._refresh_token_lifetime: int = 100 #settings.auth.refresh_token_lifetime_minutes
        self._algorithm: str = "RS256" #settings.auth.algorithm
    
    def create_jwt_token(self, user_data: UserResponce):
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_lifetime)
        payload = {
            "iss": "localhost", #settings.app.host,
            "sub": user_data.id,
            "email": user_data.email,
            "role": user_data.role,
            "exp": expire,
            "jti": str(uuid4())
        }
        
        return jwt.encode(
            payload=payload,
            key=self.private_key,
            algorithm=self.algorithm
        )
        
    def decode_jwt_token(self, token: str):
        try:
            
            decoded_payload = jwt.decode(token, self.public_key, self.algorithm)

            return decoded_payload
        
        except jwt.InvalidSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token signature is invalid"
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is not valid"
            )
        
    
    
    
obj_ = JwtManager()
user_obj = UserResponce(id=11, email="MARYKOV63@MAIL.RU", role="user")
print(obj_.create_access_token(user_data=user_obj))
        
        
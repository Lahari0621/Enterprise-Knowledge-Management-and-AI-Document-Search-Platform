import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = os.getenv('SECRET_KEY', 'development-secret')
ALGORITHM = 'HS256'
pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password):
    return pwd.hash(password)

def verify_password(password, password_hash):
    return pwd.verify(password, password_hash)

def create_token(user_id):
    return jwt.encode({'sub': str(user_id), 'exp': datetime.now(timezone.utc) + timedelta(hours=8)}, SECRET_KEY, algorithm=ALGORITHM)

def decode_user_id(token):
    try:
        return int(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub'])
    except (JWTError, KeyError, ValueError):
        return None

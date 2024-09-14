from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, Depends

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

with open("private.pem") as f:
    PRIVATE_KEY = f.read()
with open("public.pem") as f:
    PUBLIC_KEY = f.read()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload

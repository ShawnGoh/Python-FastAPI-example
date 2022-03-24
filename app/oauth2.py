from fastapi import Depends, status, HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models, schemas, database
from .config import settings

# SECRET_KEY
# Algorithm
# Expiration Time

SECRET_KEY = f"{settings.secret_key}"
ALGORITHM = f"{settings.algorithm}"
ACCESS_TOKEN_EXPIRE_MINUTES = int(f"{settings.access_token_expire_minutes}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

def create_access_token(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expiration_time})

    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_token

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY)

        id:str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id) # if token data has more fields, check here
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(token:str=Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail=f"could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_access_token(token=token, credentials_exception=credentials_exception)
    user = db.query(models.User).filter(models.User.id==token_data.id).first()

    return user
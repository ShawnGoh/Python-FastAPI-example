from .. import models, schemas, utils
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/login",
    tags=['Authentication']
)

@router.get("/", response_model=schemas.Token)
def login(user_creds:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_creds.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid Credentials")
    
    if not utils.verify(user_creds.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid Credentials")
    
    # create token
    token = oauth2.create_access_token(data={"user_id": user.id})
    # return token
    return {"access_token":token, "token_type":"bearer"}
    
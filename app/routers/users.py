from .. import models, schemas, utils
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from typing import Optional, List

router = APIRouter(
    prefix="/users",
    tags=['users']
)

# ------------------------------------------------------------------------------------------
# Users

# Create User
@router.post("/", status_code= status.HTTP_201_CREATED, response_model=schemas.UserCreateResponse) 
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash password
    hashed_pwd = utils.hash(user.password)
    user.password = hashed_pwd
    # **<classname>.dict will unpack all the contents of the json and put it into our model
    new_user = models.User(**user.dict()) 
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user) #similar to RETURNINING in normal SQL
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"Email:{user.email} is already in use")
    return new_user

# Get User Details
@router.get("/userid={id}", response_model=schemas.UserResponse) 
async def get_user(id: int, response: Response, db: Session = Depends(get_db)): #function
    user = db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"user with id={id} was not found")
    return user
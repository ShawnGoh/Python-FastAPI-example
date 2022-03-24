from sqlite3 import Cursor
import time
from typing import Optional, List
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models, schemas, utils
from .database import engine, get_db
from sqlalchemy.orm import Session



# NOTE: SQLALCHEMY DOES NOT KNOW HOW TO TALK WITH THE UNDERLYING DATABASE
# whatever database is used in whatever project, need to get the default driver for that database.
# In this case, we already have psycopg installed which works with postgresSQL


models.Base.metadata.create_all(bind=engine)

# ------------------------------------------------------------------------------------------
# Try to connect to database

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='S9830945d', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2) 

# ------------------------------------------------------------------------------------------
app = FastAPI()

@app.get("/") 
async def root(): 
    return {"message": "Welcome to my API"}

# ------------------------------------------------------------------------------------------
# Posts

# Create = POST      @app.post("/posts")
@app.post("/posts", status_code= status.HTTP_201_CREATED, response_model=schemas.Response) 
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):

    # **<classname>.dict will unpack all the contents of the json and put it into our model
    new_post = models.Post(**post.dict()) 
    db.add(new_post)
    db.commit()
    db.refresh(new_post) #similar to RETURNINING in normal SQL
    return new_post


# Read = GET       @app.get("/posts/{id}") or @app.get("/posts")
# pass in the id if want to get only 1 specific post or just a general get to get all posts
@app.get("/posts", response_model=List[schemas.Response]) 
async def get_posts(db: Session = Depends(get_db)): #function
    posts = db.query(models.Post).all()
    return posts

@app.get("/posts/postid={id}", response_model=schemas.Response) 
async def get_post(id: int, response: Response, db: Session = Depends(get_db)): #function
    post = db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id={id} was not found")
    return post
    
    
@app.get("/posts/latest", response_model=schemas.Response) 
async def get_latest(db: Session = Depends(get_db)): #function
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No posts yet")
    return post

# Update = PUT/PATCH @app.put("/posts/{id}") or @app.patch("/posts/{id}")
# use put will need to pass in all fields of the post. use patch will only need to pass in specific parts that need to be updated
@app.put("/posts/postid={id}", response_model=schemas.Response) 
async def get_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)): #function
    query = db.query(models.Post).filter(models.Post.id==id)
    dbpost = query.first()
    if dbpost == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} was not found")
    query.update(post.dict(), synchronize_session=False)
    db.commit()
    return query.first()

# Delete = DELETE    @app.delete("/posts/{id}")
@app.delete("/posts/postid={id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_post(id: int,  db: Session = Depends(get_db)): #function
    query = db.query(models.Post).filter(models.Post.id==id)
    if query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} was not found")
    query.delete(synchronize_session=False)  
    db.commit()               


# ------------------------------------------------------------------------------------------
# Users

# Create User
@app.post("/users", status_code= status.HTTP_201_CREATED, response_model=schemas.UserCreateResponse) 
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
@app.get("/users/userid={id}", response_model=schemas.UserResponse) 
async def get_user(id: int, response: Response, db: Session = Depends(get_db)): #function
    user = db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"user with id={id} was not found")
    return user
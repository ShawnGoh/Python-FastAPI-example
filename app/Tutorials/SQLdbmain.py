from sqlite3 import Cursor
import time
from typing import Optional, List
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel, PostgresDsn
from . import schemas
import psycopg2
from psycopg2.extras import RealDictCursor
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
# Create = POST      @app.post("/posts")
@app.post("/posts", status_code= status.HTTP_201_CREATED, response_model=schemas.Response) 
def create_post(post: schemas.PostCreate):
    # DO NOT USE an f string. Using an f string makes the code vulnerable to sql injection
    # Using a %s and execute would sanitise the incoming values before passing it into the SQL database
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES(%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return new_post


# Read = GET       @app.get("/posts/{id}") or @app.get("/posts")
# pass in the id if want to get only 1 specific post or just a general get to get all posts
@app.get("/posts", response_model=List[schemas.Response]) 
async def get_posts(): #function
    cursor.execute("""SELECT * FROM posts""") # To write the sql query here
    posts = cursor.fetchall()  # for returning multiple outputs from the database
    return posts

@app.get("/posts/postid={id}", response_model=schemas.Response) 
async def get_post(id: int, response: Response): #function
    cursor.execute("""SELECT * FROM posts WHERE id=%s""", (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id={id} was not found")
    return post
    
    
@app.get("/posts/latest", response_model=schemas.Response) 
async def get_latest(): #function
    cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC LIMIT 1""")
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No posts yet")
    return post


# Update = PUT/PATCH @app.put("/posts/{id}") or @app.patch("/posts/{id}")
# use put will need to pass in all fields of the post. use patch will only need to pass in specific parts that need to be updated
@app.put("/posts/postid={id}", response_model=schemas.Response) 
async def get_post(id: int, post:schemas.PostCreate): #function
    cursor.execute("""UPDATE posts SET title = %s, content= %s , published=%s WHERE id=%s RETURNING *""", (post.title, post.content, str(post.published), str(id),))
    post = cursor.fetchone()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} was not found")
    conn.commit()
    return post

# Delete = DELETE    @app.delete("/posts/{id}")
@app.delete("/posts/postid={id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_post(id: int): #function
    cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING *""", (str(id),))
    post = cursor.fetchone()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id={id} was not found")
    conn.commit()                    

# ------------------------------------------------------------------------------------------
# Create new User
@app.post("/users", status_code= status.HTTP_201_CREATED, response_model=schemas.UserCreateResponse) 
def create_user(user: schemas.UserCreate):
    # DO NOT USE an f string. Using an f string makes the code vulnerable to sql injection
    # Using a %s and execute would sanitise the incoming values before passing it into the SQL database
    new_user = None
    try:
        cursor.execute("""INSERT INTO users (email, password) VALUES(%s, %s) RETURNING * """, (user.email, user.password))
        new_user = cursor.fetchone()
        conn.commit()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"{user.email} is already in use")
    
    return new_user
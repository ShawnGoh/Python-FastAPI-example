from sqlite3 import Cursor
from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel


# ------------------------------------------------------------------------------------------
# Basics/Get Requests

# Before starting anything, make sure that the terminal and the interpreter is running in the virtual environment(venv). 
# If terminal is not running in venv, go into the venv file<< or cd into it and run the .ps1 file if on powershell or .bat file if on cmd.
# If interpreter is not running in venv, go btm right, click on the python version and change it to the venv python path.


# to start the webserver, use uvicorn <filename>:<FastAPI variable name> 
# in this case, will be uvicorn main:app --reload (reload is added for development environment so that we do not need to restart the server everytime we save the file. When push to production environment, want to remove this --reload line)
app = FastAPI()

# this is a path operation/route and it consists of 2 things: 1. decorator, 2. function
# Decorator: to link our function with the FastAPI instance. 
# Function: async call is optional, only needed if need to perform async task. Name of function does not matter, can name whatever we want
@app.get("/") #decorator = @<FastAPI variable name>.<HTTP function>("/path")
async def root(): #function
    return {"message": "Welcome to my API"}

"""
@app.get("/posts") 
async def get_posts(): #function
    return {"post1": my_posts}
"""
# ------------------------------------------------------------------------------------------
# Post Requests/Pydantic

 # In function, create a variable to store the data that will be passed through the api call and use the Body(...) from FastAPI and convert it into a python dictionary.
# @app.post("/createpost") 
# async def create_post(payLoad: dict = Body(...)):
#     print(payLoad)
#     return {"new_post": f"title:{payLoad['title']} | content:{payLoad['content']}"}

# To make sure that user/client side is sending in data we want/can interact with, we can use pydantic to do some data verfication. We can create a class that defines the schema of the incoming JSON that we expect and pass it as a parameter in the function. 

# Pydantic will then check the incoming body against the class that we have specified and fit it into the class for further reference. If the incoming body has an incorrect schema, a response will be sent to the client side to inform them of the type error.
# E.g. we want a post with the following information: 1. title(str) 2. content(str) 3. Publish post or not(bool, default = True)

my_posts = [{"title": "title of post 1", "content":"content of post 1", "id":1},
            {"title": "title of post 2", "content":"content of post 2", "id":2}]
count = 2

class Post(BaseModel):
    title: str
    content: str
    published: bool = True #optional bool field that will deafult to True if not filled.
    rating: Optional[int] = None # Optional int field that will default to None if not filled on Client side
    id: Optional[int] = None
"""
@app.post("/posts") 
def create_post2(post: Post):
    print(post)
    post.dict # converts the pydantic class to a python dictionary.
    return {"data": "new post"}

"""

# ------------------------------------------------------------------------------------------
# CRUD based application
# C reate   = POST
# R ead     = GET
# U pdate   = PUT/PATCH
# D elete   = DELETE

# Best practices/standard conventions: always use the plural for the decorator/route.

# e.g. for a posts endpoint
# C reate   = POST      @app.post("/posts")
@app.post("/posts", status_code= status.HTTP_201_CREATED) 
def create_post(post: Post):
    post_dict = post.dict()
    global count
    count+=1
    post_dict["id"] = count
    my_posts.append(post_dict) # converts the pydantic class to a python dictionary.
    return {"data": post_dict}


# R ead     = GET       @app.get("/posts/{id}") or @app.get("/posts")
# pass in the id if want to get only 1 specific post or just a general get to get all posts
@app.get("/posts") 
async def get_posts(): #function
    return {"post1": my_posts}

@app.get("/posts/postid={id}") 
async def get_post(id: int, response: Response): #function
    for i in my_posts:
        if i["id"] == id:
            return {"post details": i}
    # response.status_code = status.HTTP_404_NOT_FOUND
    # return {"message": f"post with id={id} was not found"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id={id} was not found")
    
@app.get("/posts/latest") 
async def get_post(): #function
    return {"post details": my_posts[len(my_posts)-1]}
# U pdate   = PUT/PATCH @app.put("/posts/{id}") or @app.patch("/posts/{id}")
# use put will need to pass in all fields of the post. use patch will only need to pass in specific parts that need to be updated

@app.put("/posts/postid={id}") 
async def get_post(id: int, post:Post): #function
    for i in range(len(my_posts)):
        if my_posts[i]["id"] == id:
            my_posts[i] = post.dict()
            return {"post changed": post.dict()}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id={id} was not found")
# D elete   = DELETE    @app.delete("/posts/{id}")

@app.delete("/posts/postid={id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_post(id: int): #function
    for i in range(len(my_posts)):
        if my_posts[i]["id"] == id:
            my_posts.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id={id} was not found")
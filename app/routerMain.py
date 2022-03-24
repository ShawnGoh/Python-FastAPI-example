
from . import models
from fastapi import FastAPI
from .database import engine
from .routers import posts, users, auth, vote
from fastapi.middleware.cors import CORSMiddleware

# To deploy on heroku: https://www.youtube.com/watch?v=0sOvCWFmrtA&t=41679s 
# To deploy on a ubuntuVM: https://www.youtube.com/watch?v=0sOvCWFmrtA&t=43504s 

# Before starting the api and server, make sure all dependencies are present via the command "pip install -r requirements.txt"

# you can choose to do this in a virtual environment via the command "python3 -m venv" in the path that you want to start the virtual environment in.

# To start the api and server, cd to the top level path "PYTHON API DEVELOPMENT" and run the uvicorn command below.

# NOTE: SQLALCHEMY DOES NOT KNOW HOW TO TALK WITH THE UNDERLYING DATABASE
# whatever database is used in whatever project, need to get the default driver for that database.
# In this case, we already have psycopg installed which works with postgresSQL

# To start server: uvicorn app.routerMain:app --reload



# models.Base.metadata.create_all(bind=engine)

# ------------------------------------------------------------------------------------------
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/") 
async def root(): 
    return {"message": "Welcome to my API"}


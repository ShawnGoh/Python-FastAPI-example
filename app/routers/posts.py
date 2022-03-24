from app.oauth2 import get_current_user
from .. import models, schemas, utils, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['posts']
)

# ------------------------------------------------------------------------------------------
# Posts

# Create = POST      @app.post("/posts")
@router.post("/", status_code= status.HTTP_201_CREATED, response_model=schemas.Response) 
def create_post(post: schemas.PostCreate, current_user: models.User = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    # **<classname>.dict will unpack all the contents of the json and put it into our model
    npost = post.dict()
    npost["user_id"]=current_user.id
    new_post = models.Post(**npost) 
    db.add(new_post)
    db.commit()
    db.refresh(new_post) #similar to RETURNINING in normal SQL
    return new_post


# Read = GET       @app.get("/posts/{id}") or @app.get("/posts")
# pass in the id if want to get only 1 specific post or just a general get to get all posts
@router.get("/", response_model=List[schemas.newPost]) 
async def get_posts(db: Session = Depends(get_db), limit:int = 10, skip:int = 0, search: Optional[str] = ""): #function
    # posts = db.query(models.Post).filter(models.Post.published == True, models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # SQLAlchemy default join is a LEFT INNER JOIN. Need to modify if need other joins
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.published == True, models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return results

@router.get("/myposts", response_model=List[schemas.newPost]) 
async def get_my_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.user_id == current_user.id).all()
    return posts

@router.get("/postid={id}", response_model=schemas.newPost) 
async def get_post(id: int, response: Response, db: Session = Depends(get_db)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id={id} was not found")
    return post
    
    
@router.get("/latest", response_model=schemas.newPost) 
async def get_latest(db: Session = Depends(get_db)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).order_by(models.Post.created_at.desc()).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No posts yet")
    return post


# Update = PUT/PATCH @app.put("/posts/{id}") or @app.patch("/posts/{id}")
# use put will need to pass in all fields of the post. use patch will only need to pass in specific parts that need to be updated
@router.put("/postid={id}", response_model=schemas.Response) 
async def get_post(id: int, post: schemas.PostCreate, current_user: models.User = Depends(oauth2.get_current_user), db: Session = Depends(get_db)): #function
    query = db.query(models.Post).filter(models.Post.id==id)
    dbpost = query.first()
    if dbpost == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} was not found")
    if dbpost.user_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not own post {id}")
    query.update(post.dict(), synchronize_session=False)
    db.commit()
    return query.first()

# Delete = DELETE    @app.delete("/posts/{id}")
@router.delete("/postid={id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_post(id: int, current_user: models.User = Depends(oauth2.get_current_user),  db: Session = Depends(get_db)): #function
    query = db.query(models.Post).filter(models.Post.id==id)
    dbpost = query.first() 
    if dbpost == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} was not found")
    if dbpost.user_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not own post {id}")
    query.delete(synchronize_session=False)  
    db.commit()               

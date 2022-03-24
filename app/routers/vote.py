from .. import models, schemas, utils, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


router = APIRouter(
    prefix="/votes",
    tags=['Votes']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def login(vote: schemas.Vote, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # Check if post exists
    postquery = db.query(models.Post).filter(models.Post.id == vote.post_id)
    # If post does not exist, throw exception
    if not postquery.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {vote.post_id} does not exist")

    # Else, continue
    query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id== current_user.id)
    foundvote = query.first()

    # if vote direction = 1, means user is liking the post
    if vote.vote_dir == 1:
        # check if user has already liked the post before, if liked before, throw error
        if foundvote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"user {current_user.id} has already voted on post {vote.post_id}")
        # else, vote by sending a new entry to the Vote db
        new_vote = models.Vote(post_id=vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully added vote"}
    # if vote direction = 0, means user is unliking the post
    elif vote.vote_dir == 0:
        # check if user has already liked the post before, if never liked before, throw error
        if not foundvote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"vote on post {vote.post_id} does not exist")
        # else, remove vote from the Vote db
        query.delete(synchronize_session=False)
        db.commit()
        return {"message": "successfully deleted vote"}
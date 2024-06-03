from fastapi import HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import model, schemas, oauth2
from typing import List, Optional
from ..database import get_db

router = APIRouter(prefix="/votes", tags=["Votes"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_votes(
    votes: schemas.Votes,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post_query = db.query(model.Post).filter(model.Post.id == votes.post_id)
    post = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist"
        )
    vote_query = db.query(model.Vote).filter(
        model.Vote.post_id == votes.post_id, model.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()
    if votes.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.email} has already voted on the post{votes.post_id}",
            )
        new_vote = model.Vote(user_id=current_user.id, post_id=votes.post_id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added vote"}
    if votes.dir == 0:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist"
            )
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully deleted vote"}

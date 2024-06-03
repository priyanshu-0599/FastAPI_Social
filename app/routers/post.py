from fastapi import HTTPException, Response, status, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import model, schemas, oauth2
from typing import List, Optional
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.PostVoteOut])
async def get_posts(
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    print(current_user.email)
    # # posts = db.query(model.Posts).filter(model.Posts.user_id == current_user.id).all() #Can view posts that have been created by the logged in user
    # posts = (
    #     db.query(model.Post)
    #     .filter(model.Post.title.contains(search))
    #     .order_by(model.Post.id)
    #     .limit(limit)
    #     .offset(skip)
    #     .all()
    # )
    posts = (
        db.query(model.Post, func.count(model.Vote.post_id).label("votes"))
        .join(model.Vote, model.Vote.post_id == model.Post.id, isouter=True)
        .group_by(model.Post.id)
        .filter(model.Post.title.contains(search))
        .order_by(model.Post.id)
        .limit(limit)
        .offset(skip)
        .all()
    )
    return posts


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
async def create_posts(
    posts: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    # new_post = model.Post(
    #     title=posts.title,
    #     content=posts.content,
    #     published=posts.published,
    #     rating=posts.rating,
    # )
    print(current_user.email)
    new_post = model.Post(user_id=current_user.id, **posts.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostVoteOut)
async def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    print(current_user.email)
    post_query = (
        db.query(model.Post, func.count(model.Vote.post_id).label("votes"))
        .join(model.Vote, model.Vote.post_id == model.Post.id, isouter=True)
        .group_by(model.Post.id)
        .filter(model.Post.id == id)
    )
    post = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with that id: {id} Not found",
        )
    # if post.user_id != current_user.id:  #Can view single post that have only been created by the logged in user
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to perform requested action",
    #     )
    return post


@router.put(
    "/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.PostResponse,
)
async def update_post(
    id: int,
    posts: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    print(current_user.email)
    post_query = db.query(model.Post).filter(model.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with that id: {id} Not found",
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    post_query.update(posts.model_dump(), synchronize_session=False)
    db.commit()
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    print(current_user.email)
    post_query = db.query(model.Post).filter(model.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with that id: {id} Not found",
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

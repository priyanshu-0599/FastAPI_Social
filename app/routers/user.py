from fastapi import APIRouter, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from .. import model, schemas, utils
from ..database import get_db
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(model.User).order_by(model.User.id).all()
    return users


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse
)
async def create_users(users: schemas.UserCreate, db: Session = Depends(get_db)):
    # new_user = model.Users(
    #     email=users.email,
    #     password=users.password
    # )
    hashed_password = utils.hash_password(users.password)
    users.password = hashed_password
    new_user = model.User(**users.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.UserResponse)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with that id: {id} Not found",
        )
    return user


@router.put(
    "/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.UserResponse,
)
async def update_user(
    id: int, users: schemas.UserCreate, db: Session = Depends(get_db)
):
    updated_users = db.query(model.User).filter(model.User.id == id)
    if updated_users.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with that id: {id} Not found",
        )
    updated_users.update(users.model_dump(), synchronize_session=False)
    db.commit()
    return updated_users.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db: Session = Depends(get_db)):
    del_user = db.query(model.User).filter(model.User.id == id)
    if del_user.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with that id: {id} Not found",
        )
    del_user.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, model, utils, oauth2


router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(model.User)
        .filter(model.User.email == user_credentials.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    access_token = oauth2.create_access_token(
        data={"user_id": user.id, "timestamp": str(user.timestamp)}
    )
    return {"access_token": access_token, "token_type": "bearer"}

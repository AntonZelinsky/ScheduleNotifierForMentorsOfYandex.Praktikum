from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import services
from core.database import get_db

from .. import schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
          skip: int = 0,
          limit: int = 100,
          db: Session = Depends(get_db),
):
    users = services.get_users(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate,
                db: Session = Depends(get_db)
                ):
    db_user = services.get_user_by_telegram_id(db, telegram_id=user.telegram_id)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="User already registered",
        )
    return services.create_user(db=db, user=user)

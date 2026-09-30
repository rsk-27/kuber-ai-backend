from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse


router = APIRouter()


@router.post("/users", response_model=UserResponse)
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db)
):
    user = User(
        name=request.name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
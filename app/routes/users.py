from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, crud, dependencies

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserRead)
def read_my_profile(
    current: models.User = Depends(dependencies.get_current_user),
):
    return current


@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user_profile(
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):
    """
    - Admin: może odczytać profil każdego usera
    - User: tylko swój profil
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not current.is_admin and current.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return user


@router.get("/", response_model=List[schemas.UserRead])
def list_users(
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):
    """
    - Admin: może zobaczyć wszytkich userów
    - User: nie ma dostępu do tej funkcji
    """
    if not current.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return db.query(models.User).all()

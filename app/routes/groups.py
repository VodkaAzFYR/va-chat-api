from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import exc
from typing import List

from .. import models, schemas, crud, dependencies

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=schemas.GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(
    group_in: schemas.GroupCreate,
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):
    """
    - Każdy user może utworzyć nową grupę
    - Automatycznie dodaje go do tej grupy jak twórca
    """
    
    try:
        group = crud.create_group(db, group_in, current.id)
    except exc.IntegrityError as e:

        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Group with name '{group_in.name}' already exists"
        )

    group.members.append(current)
    db.commit()
    db.refresh(group)
    return group


@router.get("/", response_model=List[schemas.GroupRead])
def list_groups(
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):
    """
    - Admin: zwraca wszystkie grupy
    - User: tylko grupy do których należy
    """
    if current.is_admin:
        return db.query(models.Group).all()
    return current.groups


@router.get("/{group_id}", response_model=schemas.GroupReadWithMembers)
def read_group(
    group_id: int,
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):
    """
    - Admin: może zobaczyć dowolną grupę
    - User: tylko jeśli należy do tej grupy
    """
    group = crud.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    
    if not current.is_admin and all(g.id != group_id for g in current.groups):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return group


@router.post("/{group_id}/add-user/{new_user_id}", status_code=status.HTTP_200_OK)
def add_user_to_group(
    group_id: int,
    new_user_id: int,
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):
    """
    - Admin: może dodać usera do dowolnej grupy
    - User: tylko jeśli należy do tej grupy
    """
    group = crud.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    
    if not current.is_admin and all(g.id != group_id for g in current.groups):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    user_to_add = crud.get_user(db, new_user_id)
    if not user_to_add:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if any(u.id == new_user_id for u in group.members):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already in group"
        )

    group.members.append(user_to_add)
    db.commit()
    return {"msg": "User added to group"}


@router.post("/{group_id}/remove-user/{remove_user_id}", status_code=status.HTTP_200_OK)
def remove_user_from_group(
    group_id: int,
    remove_user_id: int,
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):
    """
    - Admin: może usunąć usera z dowolnej grupy
    - User: tylko jeśli należy do tej grupy
    """
    group = crud.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    
    if not current.is_admin and all(g.id != group_id for g in current.groups):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    user_to_remove = crud.get_user(db, remove_user_id)
    if not user_to_remove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if all(g.id != group_id for g in user_to_remove.groups):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not in group")

    group.members.remove(user_to_remove)
    db.commit()
    return {"msg": "User removed from group"}


@router.delete("/{group_id}", status_code=status.HTTP_200_OK)
def delete_group(
    group_id: int,
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):
    """
    - Admin: może usunąć każdą grupę
    - User: może usunąć tylko grupy które sam utworzył
    """
    group = crud.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if not current.is_admin and group.creator_id != current.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    crud.delete_group(db, group_id)
    return {"msg": "Group deleted"}

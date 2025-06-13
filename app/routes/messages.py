from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, crud, dependencies

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/private/{other_user_id}", response_model=List[schemas.MessageRead])
def read_private_messages(
    other_user_id: int,
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):
    other = crud.get_user(db, other_user_id)
    if not other:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not current.is_admin and current.id != other_user_id:
        pass  

    msgs = crud.get_private_messages(db, current.id, other_user_id)
    return msgs


@router.post("/private/{other_user_id}", response_model=schemas.MessageRead, status_code=status.HTTP_201_CREATED)
def send_private_message(
    other_user_id: int,
    msg_in: schemas.PrivateMessageCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):

    other = crud.get_user(db, other_user_id)
    if not other:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    m = crud.create_private_message(
        db,
        sender_id=current_user.id,
        receiver_id=other_user_id,
        content=msg_in.content,
    )
    return m


@router.get("/group/{chat_id}", response_model=List[schemas.MessageRead])
def read_group_messages(
    chat_id: int,
    db: Session = Depends(dependencies.get_db),
    current: models.User = Depends(dependencies.get_current_user),
):

    group = crud.get_group(db, chat_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if not current.is_admin and all(g.id != chat_id for g in current.groups):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return crud.get_group_messages(db, chat_id)


@router.post("/group/{chat_id}", response_model=schemas.MessageRead, status_code=status.HTTP_201_CREATED)
def send_group_message(
    chat_id: int,
    msg_in: schemas.GroupMessageCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):

    
    group = crud.get_group(db, chat_id)

    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if not current_user.is_admin and all(g.id != chat_id for g in current_user.groups):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    m = crud.create_group_message(
        db,
        sender_id=current_user.id,
        group_id=chat_id,
        content=msg_in.content,
    )
    return m

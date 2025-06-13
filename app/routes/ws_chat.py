import json
from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from .. import crud, models, dependencies

router = APIRouter(tags=["ws"])

active_private_connections: dict[int, WebSocket] = {}
active_group_connections: dict[int, set[WebSocket]] = {}


@router.websocket("/ws/chat")
async def ws_chat(
    websocket: WebSocket,
    token: str,
    chat_type: str,  
    chat_id: int,    
    db: Session = Depends(dependencies.get_db),
):
    try:
        payload = dependencies.auth.verify_access_token(token)
        current_user = crud.get_user(db, payload.get("user_id"))
        if current_user is None:
            raise ValueError("Użytkownik nie istnieje")
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    if chat_type == "private":
        other = crud.get_user(db, chat_id)
        if not other:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    elif chat_type == "group":
        group = crud.get_group(db, chat_id)
        if not group:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        if not current_user.is_admin and all(g.id != chat_id for g in current_user.groups):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    else:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    if chat_type == "private":
        active_private_connections[current_user.id] = websocket
    else:
        if chat_id not in active_group_connections:
            active_group_connections[chat_id] = set()
        active_group_connections[chat_id].add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            obj = json.loads(data)
            content = obj.get("content", "").strip()
            if not content:
                await websocket.send_json({"error": "Message content cannot be empty"})
                continue
            if chat_type == "private":
                m = crud.create_private_message(
                    db,
                    sender_id=current_user.id,
                    receiver_id=chat_id,
                    content=content,
                )
            else:
                m = crud.create_group_message(
                    db,
                    sender_id=current_user.id,
                    group_id=chat_id,
                    content=content,
                )
            payload_to_send = {
                "id": m.id,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
                "sender_id": m.sender_id or m.user_id,
                "receiver_id": m.receiver_id,  
                "group_id": m.group_id,        
            }

            if chat_type == "private":
                await websocket.send_json(payload_to_send)
                recipient_ws = active_private_connections.get(chat_id)
                if recipient_ws:
                    try:
                        await recipient_ws.send_json(payload_to_send)
                    except:
                        active_private_connections.pop(chat_id, None)
            else:
                recipients = active_group_connections.get(chat_id, set())
                to_remove = []
                for ws in recipients:
                    try:
                        await ws.send_json(payload_to_send)
                    except:
                        
                        to_remove.append(ws)
                
                for ws in to_remove:
                    recipients.discard(ws)
    except WebSocketDisconnect:
        if chat_type == "private":
            active_private_connections.pop(current_user.id, None)
        else:
            conns = active_group_connections.get(chat_id)
            if conns and websocket in conns:
                conns.discard(websocket)
        return

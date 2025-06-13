from fastapi import FastAPI
from .database import engine, Base
from .routes import auth, users, groups, messages
from .routes.ws_chat import router as ws_router  


Base.metadata.create_all(bind=engine)

app = FastAPI(title="VA Chat API")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(messages.router)
app.include_router(ws_router)

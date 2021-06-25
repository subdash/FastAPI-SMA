"""
POST /register                      -> receive a passphrase, hash it, store the hash and create a user
POST /login                         -> compare hashed passphrase to stored hash and authenticate user
GET  /friends                       -> get list of friends on key ring
POST /friends                       -> add key to keyring
GET  /messages/                     -> get encrypted messages and show previews
GET  /messages/{uid}                -> return single encrypted message
POST /messages/{uid}                -> send encrypted message
GET  /messages/{uid}/file/{file_id} -> receive an encrypted file
POST /messages/{uid}/file/{file_id} -> send an encrypted file
"""
from fastapi import FastAPI

from src.definitions import tags_metadata
from src.server.core.models import models
from src.server.core.models.database import engine
from src.server.v1.endpoints import messages, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SMA (Secure Messaging App)",
    description="A messaging app written in Python that supports end to end"
                "encryption using GNU Privacy guard.",
    version="1.0.0",
    openapi_tags=tags_metadata
)
app.include_router(user.router)
app.include_router(messages.router)

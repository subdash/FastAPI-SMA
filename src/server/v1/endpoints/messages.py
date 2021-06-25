from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.server.core.models import crud
from src.server.core.models.models import User
from src.server.core.schemas import schema
from src.server.core.schemas.schema import MessageBase
from src.server.v1.dependencies import get_current_user, get_db
from src.server.v1.exceptions import HTTPNotYetImplemented

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)


@router.get("/", response_model=List[schema.ConversationMessage])
async def get_conversations(current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    """
    Returns the most recent message for each user that the authenticated one
    has corresponded with. The message content is truncated so that the user
    can easily see multiple conversation previews at once.

    :param current_user: Currently authenticated user's account data
    :param db: DB session
    :return: List of message previews for each user that the authenticated one
    has corresponded with
    """
    return crud.get_conversation_previews(db, current_user.id)


@router.get("/{friend_id}", response_model=List[schema.ConversationMessage])
async def get_conversation(friend_id: int,
                           current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """
    Returns all messages between the currently authenticated user and a user
    who they have sent messages to.

    :param friend_id: The ID of the user whose correspondence is being displayed
    :param current_user: Currently authenticated user's account data
    :param db: DB session
    :return: A list of messages to be displayed
    """
    return crud.get_one_conversation(db,
                                     reader_id=current_user.id,
                                     friend_id=friend_id)


@router.post("/{friend_id}", response_model=List[schema.ConversationMessage])
async def send_message(friend_id: int,
                       message: MessageBase,
                       current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """
    This endpoint creates a new message instance in the database and then
    returns a list of all messages between the sender and recipient so that
    the conversation can be displayed to the client. It may be better to limit
    the responsibility of this function to creating a message, but if that
    approach was taken, two REST calls instead of one would have to be made.

    :param friend_id: The ID of the user to send a message to
    :param message: The message to send
    :param current_user: Currently authenticated user's account data
    :param db: DB session
    :return: Returns the correspondence between the sender and recipient after
    the message has been sent
    """
    crud.create_message(db,
                        sender=current_user.id,
                        recipient=friend_id,
                        content=message.content)

    return crud.get_one_conversation(db, reader_id=current_user.id,
                                     friend_id=friend_id)


@router.get("/{friend_id}/file/{file_id}")
async def receive_file():
    raise HTTPNotYetImplemented


@router.post("/{friend_id}/file/{file_id}")
async def send_file():
    raise HTTPNotYetImplemented

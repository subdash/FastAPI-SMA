from datetime import datetime
from typing import List, Dict

from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.server.core.models import models
from src.server.core.schemas import schema
from src.server.v1.exceptions import HTTPInvalidEmailQuery
from src.server.v1.exceptions import HTTPInvalidUsernameQuery


################################################################################
# User
################################################################################
def get_user_by_username(db: Session, username: str) -> models.User:
    """
    Look up a user in the database by username.

    :param db: DB session
    :param username: Username to look up user by
    :return: A User record if there is a match
    """
    predicate = models.User.username == username
    return db.query(models.User).filter(predicate).first()


def get_user_by_email(db: Session, email: str) -> models.User:
    """
    Look up a user in the database by email.

    :param db: DB session
    :param email: Email to look up user by
    :return: A User record if there is a match
    """
    predicate = models.User.email == email
    return db.query(models.User).filter(predicate).first()


def create_user(db: Session, user: schema.UserCreate) -> models.User:
    """
    Take account creation data, hash the password and store the new user in the
    database.

    :param db: DB session
    :param user: User info for account creation
    :return: Created user
    """
    def get_password_hash(password):
        # TODO: Update from bcrypt to Argon2
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username,
                          email=user.email,
                          hashed_password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_name_email_pairs(db: Session) -> List[schema.UserBase]:
    """
    Get the username and email of all users in the DB. This is not scalable,
    but works for a small number of users. See comments about add-friend
    functionality in user.py.

    :param db: DB session
    :return: List of username/email pairs
    """
    result = db.query(models.User.username, models.User.email).all()

    return result


def lookup_friend_id_by_email(db: Session, email: str) -> Dict[str, int]:
    """
    Pretty self explanatory: search for a user's ID by email.

    :param db: DB session
    :param email: Email to look up user ID by
    :return: The ID of the user if the email is in the database
    """
    result = db.query(models.User.id) \
        .filter(models.User.email == email) \
        .first()

    if result is None:
        raise HTTPInvalidEmailQuery

    return {"id": result.id}


def lookup_friend_id_by_username(db: Session, username: str):
    """
    Also pretty self explanatory: search for a user's ID by username.

    :param db: DB session
    :param username: Username to look up user ID by
    :return: The ID of the user if the username is in the database
    """
    result = db.query(models.User.id) \
        .filter(models.User.username == username) \
        .first()

    if result is None:
        raise HTTPInvalidUsernameQuery

    return {"id": result.id}


################################################################################
# Message/Conversation
################################################################################
def _map_message(message: models.Message) -> schema.ConversationMessage:
    """
    Takes a message record and returns an object with the usernames of the
    sender and recipient, as well as the message content and time sent. The
    first three of those are not stored in the message table.

    :param message: A database record of a message (id, time sent, content)
    :return: A human readable message object
    """
    return schema.ConversationMessage(sender=message.sender.username,
                                      recipient=message.recipient.username,
                                      content=message.message.content,
                                      time_sent=message.message.time_sent)


def _truncate_message(
        message: schema.ConversationMessage
) -> schema.ConversationMessage:
    """
    This function simply truncates the content of a message if it is too long
    so it can be displayed as a preview. This docstring also acknowledges the
    horrendous ugliness of the function signature here.

    :param message: Message to be truncated
    :return: Message after truncation
    """
    if len(message.content) > 19:
        message.content = message.content[:20] + "..."

    return message


def create_message(db: Session,
                   sender: int,
                   recipient: int,
                   content: str) -> models.Message:
    """
    Creates a Message record in the database and returns it.

    :param db: DB session
    :param sender: ID of user sending the message
    :param recipient: ID of user receiving the message
    :param content: The actual message content being sent
    :return: The message after it has been stored in the database
    """
    db_message = models.Message(time_sent=datetime.now(), content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    db_conversation = models.Conversation(sender_id=sender,
                                          recipient_id=recipient,
                                          message_id=db_message.id)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return db_message


def get_one_conversation(db: Session,
                         reader_id: int,
                         friend_id: int) -> List[schema.ConversationMessage]:
    """
    Here, we are going to query the conversation table twice. This could probably
    be done in one query, but for simplicity's sake it's done this way. The
    conversation table only has the sender id, recipient id and message id. We
    want to get all rows where the sender id and recipient id match the users
    whose correspondence we want to return. Once all of those records are
    retrieved, we can extract the sender, recipient and message from each one
    because of the relationship defined in the SQLAlchemy model. All get sorted
    by time sent and are returned in a list.

    Example response:
    [
        {
            "sender": "Mia",
            "recipient": "Dash",
            "content": "Hi!",
            "time_sent": "2021-06-18T11:11:11"
        },
        {
            "sender": "Dash",
            "recipient": "Mia",
            "content": "Oh hello there",
            "time_sent": "2021-06-18T12:12:12"
        }
    ]

    :param db: DB session
    :param reader_id: The user reading the messages
    :param friend_id: The other user whose correspondence is being viewed
    :return: A list of messages
    """
    messages_sent = db.query(models.Conversation) \
        .filter(models.Conversation.sender_id == reader_id) \
        .filter(models.Conversation.recipient_id == friend_id) \
        .all()

    if reader_id == friend_id:
        # If you're reading your own messages to yourself, avoid duplicates
        messages_received = []

    else:
        messages_received = db.query(models.Conversation) \
            .filter(models.Conversation.sender_id == friend_id) \
            .filter(models.Conversation.recipient_id == reader_id) \
            .all()

    # Map each conversation record to a message object
    response = list(map(lambda msg: _map_message(msg),
                        messages_sent + messages_received))

    response.sort(key=lambda obj: obj.time_sent)

    return response


def get_conversation_previews(
        db: Session,
        reader_id: int
) -> List[schema.ConversationMessage]:
    """
    Get only the most recent message for each person you have corresponded with
    and truncate the message content if it is too long to show a preview.

    :param db: DB session
    :param reader_id: ID of the user viewing their messages
    :return: A preview of the most recent message between the user and every
    other user they have messaged
    """
    most_recent_messages = db.query(models.Conversation,
                                    func.max(models.Message.time_sent)) \
        .group_by(models.Conversation.sender_id) \
        .filter(models.Message.id == models.Conversation.message_id) \
        .filter(models.Conversation.sender_id != reader_id) \
        .all()

    # We only want the conversation object (row[0]), not the time_sent
    conversation_records = list(map(lambda row: row[0], most_recent_messages))
    response = list(map(lambda msg: _map_message(msg), conversation_records))
    response.sort(key=lambda obj: obj.time_sent)

    response = [_truncate_message(msg) for msg in response]

    return response

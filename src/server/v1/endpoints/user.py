from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.definitions import ACCESS_TOKEN_EXPIRE_MINUTES
from src.server.core.models import crud
from src.server.core.schemas import schema
from src.server.core.schemas.schema import UserBase, UserLookup, User, UserId
from src.server.v1.dependencies import get_db, get_current_user
from src.server.v1.exceptions import HTTPBadCredentials, HTTPInvalidUserQuery
from src.server.v1.exceptions import HTTPEmailAlreadyRegistered
from src.server.v1.exceptions import HTTPNotYetImplemented
from src.server.v1.exceptions import HTTPUsernameAlreadyRegistered
from src.server.v1.misc import authenticate_user, create_access_token

router = APIRouter(
    prefix="",
    tags=["user"]
)


@router.post("/register")
async def register(user: schema.UserCreate,
                   db: Session = Depends(get_db)) -> JSONResponse:
    """
    Creates a new user account in the database.

    :param user: A User object to create an account with
    :param db: DB session
    :return: Empty JSON response when successful
    """
    existing_user = crud.get_user_by_username(db, username=user.username)
    existing_email = crud.get_user_by_email(db, email=user.email)

    if existing_user:
        raise HTTPUsernameAlreadyRegistered

    if existing_email:
        raise HTTPEmailAlreadyRegistered

    crud.create_user(db=db, user=user)

    return JSONResponse(content={})


@router.post("/login")
async def login(db: Session = Depends(get_db),
                form_data: OAuth2PasswordRequestForm = Depends()
                ) -> JSONResponse:
    """
    Authenticates a user.

    :param db: DB session
    :param form_data: Username/password
    :return: An access token when successful
    """
    auth_user = authenticate_user(form_data.username, form_data.password, db)

    if not auth_user:
        raise HTTPBadCredentials

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": auth_user.username},
        expires_delta=access_token_expires
    )

    return JSONResponse(content={"access_token": access_token,
                                 "token_type": "bearer"})


@router.get("/friends", response_model=List[UserBase])
async def get_friends(_: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    """
    If this was a fully functional messaging app, this would only return the
    accounts that the user has added as friends. Since the add-friend
    functionality has not been implemented yet, this currently just returns
    the username/email pairs for all user accounts.

    :param _: Dependency to ensure the user is authenticated
    :param db: DB session
    :return: A list of objects containing the username and email for each
    account
    """
    # Need a way to map GPG keys to users in DB
    pairs = crud.get_name_email_pairs(db)
    return pairs


@router.post("/friends")
async def add_friend():
    # Need a way to map GPG keys to users in DB
    raise HTTPNotYetImplemented


@router.post("/lookup/", response_model=UserId)
async def lookup_friend_id(user: UserLookup,
                           _: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """
    Retrieves the user ID of a user matching a certain username or email. This
    is used when sending messages, since the client is not aware of user IDs.
    Once add-friend functionality is implemented, the client would probably
    keep track of user IDs for their friends and this function's utility would
    be obviated.

    :param user: Username or email to lookup user by
    :param _: Dependency to ensure the user is authenticated
    :param db: DB Session
    :return: The ID of the user in the database if a match is found
    """
    if user.email:
        return crud.lookup_friend_id_by_email(db, user.email)
    elif user.username:
        return crud.lookup_friend_id_by_username(db, user.username)
    else:
        raise HTTPInvalidUserQuery

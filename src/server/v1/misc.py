from datetime import timedelta, datetime
from typing import Optional, Union

from fastapi import Depends
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.definitions import ALGORITHM, config
from src.server.core.models import crud, models
from src.server.v1.dependencies import get_db


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plaintext password matches the hashed password in the DB.

    :param plain_password: Plaintext password
    :param hashed_password: Hashed password
    :return: Boolean result indicating if they match
    """
    # TODO: Update from bcrypt to Argon2
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str,
                      password: str,
                      db: Session = Depends(get_db)
                      ) -> Union[models.User, bool]:
    """
    Authenticate a user.

    :param username: Name associated with account
    :param password: Password used to authenticate
    :param db: DB session
    :return: User account or False if authentication fails
    """
    auth_user = crud.get_user_by_username(db, username)

    if auth_user and verify_password(password, auth_user.hashed_password):
        return auth_user

    return False


def create_access_token(data: dict,
                        expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token for when authentication is successful.

    :param data: Username and expiry
    :param expires_delta: Optional expiry delta for the token
    :return: The access token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta
                                  else timedelta(minutes=15))

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,
                             config['SECRET_KEY'], algorithm=ALGORITHM)

    return encoded_jwt

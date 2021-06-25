from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from src.definitions import config, ALGORITHM
from src.server.core.models import crud
from src.server.core.models.database import SessionLocal
from src.server.core.schemas.schema import TokenData, User
from src.server.v1.exceptions import HTTPBadCredentials

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    """
    Dependency to get db session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(db: Session = Depends(get_db),
                           token: str = Depends(oauth2_scheme)
                           ) -> Optional[User]:
    """
    Attempt to get the currently authenticated user. Can be used as a
    dependency to simply verify that the user is logged in, or to retrieve
    their information to be used in a DB or REST call.

    :param db: DS session
    :param token: OAuth access token
    :return: Currently authenticated user
    """
    try:
        payload = jwt.decode(token, config['SECRET_KEY'], algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPBadCredentials

        token_data = TokenData(username=username)

    except JWTError as e:
        print(e)
        raise HTTPBadCredentials

    user = crud.get_user_by_username(db, username=token_data.username)

    if user is None:
        raise HTTPBadCredentials

    return user

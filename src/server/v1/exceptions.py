from fastapi import HTTPException
from starlette import status

HTTPNotYetImplemented = HTTPException(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    detail="Not yet implemented."
)

HTTPUsernameAlreadyRegistered = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Username already registered"
)

HTTPEmailAlreadyRegistered = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already registered"
)

HTTPBadCredentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password.",
    headers={"WWW-Authenticate": "Bearer"}
)

HTTPInvalidUsernameQuery = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="The provided username was not found.",
)

HTTPInvalidEmailQuery = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="The provided email was not found.",
)

HTTPInvalidUserQuery = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Invalid user query.",
)

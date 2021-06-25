import os

from dotenv import dotenv_values

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config = {**dotenv_values(f"{ROOT_DIR}/.env")}
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

tags_metadata = [
    {
        "name": "user",
        "description": "Operations directly relating to a user's account"
    },
    {
        "name": "messages",
        "description": "Operations directly related to messaging."
    },
]

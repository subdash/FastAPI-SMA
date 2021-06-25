from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.definitions import config

sql_user = config['USER']
sql_pass = config['PASSWORD']
database = config['DB']
SQLALCHEMY_DATABASE_URL = f"mariadb+mariadbconnector://{sql_user}:{sql_pass}@127.0.0.1:3306/{database}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Each instance of SessionLocal will be a DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This class will be extended to create the DB models
Base = declarative_base()

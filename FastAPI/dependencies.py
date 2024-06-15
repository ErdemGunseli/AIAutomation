from typing import Annotated, Optional, Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from exceptions import JWTException, UserNotFoundException
from database import SessionLocal
from models import User
from security import HASH_SECRET_KEY, HASH_ALGORITHM


# Using a generator as a context manager to manage the DB session:
def get_db() -> Generator[Session, None, None]:

    # Creating a new session to connect to the DB, using the session factory:
    db = SessionLocal()
    try:
        # Providing a DB session to the caller:
        yield db
    
    except Exception:
        # Rolling back any changes if an error occurs:
        db.rollback()
        raise
    
    finally:
        # This code only runs after the function calling get_db completes, 
        # allowing the connection to be closed when no longer needed (and not too soon):
        db.close()


# Dependency Injection - if an object of type db_dependency (which is of type Session) is not provided, 
# FastAPI will automatically call get_db to obtain a DB session.
db_dependency = Annotated[Session, Depends(get_db)]


# For the authentication dependency, the OAuth2PasswordRequestForm class must be instantiated:
auth_dependency = Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]


# Instantiating OAuth2PasswordBearer with the token-generating endpoint URL as a kwarg:
token_dependency = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="auth/token"))]


async def get_current_user(db: db_dependency, token: token_dependency) -> User:
    try:
        # Attempting to decode the token using the secret key and algorithm:
        # (If successful, this will return a dictionary that contains the user data.)
        payload = jwt.decode(token, HASH_SECRET_KEY, algorithms=[HASH_ALGORITHM])

        # Extracting the user id from the payload dictionary:
        # The subject of a JWT needs to be a string, so converting back to integer:
        user_id: Optional[int] = int(payload.get("sub"))

        if user_id is None: raise JWTError

    except JWTError as e: raise JWTException from e

    return get_user(db, user_id)


def get_user(db: db_dependency, user_id: int) -> User:
    user = db.query(User).filter_by(id=user_id).first()
    if user is None: raise UserNotFoundException
    return user

user_dependency = Annotated[dict, Depends(get_current_user)]

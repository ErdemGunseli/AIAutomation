from exceptions import UserNotFoundException, InvalidCredentialsException
from dependencies import db_dependency, auth_dependency
from models import User
from security import bcrypt_context, create_access_token


def authenticate_user(db: db_dependency, email: str, password: str) -> User:
    # Searching for a user of the given email:
    user = db.query(User).filter_by(email=email).first()

    if user is None: raise UserNotFoundException
    elif not bcrypt_context.verify(password, user.password): raise InvalidCredentialsException
    return user


def login_and_generate_token(db: db_dependency, auth_form: auth_dependency) -> dict:
    # auth_form is of type OAuth2PasswordRequestForm, so it has attributes username and password.
    # In this case, username represents the user's email:
    user = authenticate_user(db, auth_form.username, auth_form.password)

    token = create_access_token(user.id)

    # 'bearer' indicates a request should be authenticated using the provided access token:
    return {"access_token": token, "token_type": "bearer"}
    
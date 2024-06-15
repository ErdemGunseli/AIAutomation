import re
import requests

from sqlalchemy.exc import IntegrityError

from exceptions import UserExistsException, InvalidPostcodeException
from database import create_system_message
from dependencies import db_dependency
from schemas import CreateUserRequest
from models import User
from security import bcrypt_context


def create_user(db: db_dependency, user_data: CreateUserRequest) -> User:
    # Hashing the password:
    password_hash = bcrypt_context.hash(user_data.password)

    # Obtaining the outer postcode:
    outer_postcode = get_outer_postcode(user_data.postcode)

    # Creating a new user instance with their name formatted, and the hashed password instead of plaintext:
    new_user = User(**user_data.model_dump(exclude={"password", "name", "postcode"}), name=user_data.name.title(), password=password_hash, postcode=outer_postcode)

    try: 
        # Returning the new user (will be converted to the response model at the endpoints):
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Inserting a system message to provide the user's details to the LLM:
        create_system_message(db, f"User's Name: {new_user.name}, User's ID: {new_user.id}, UK Outer Postcode: {outer_postcode} ", new_user.id)

        return new_user
        
    except IntegrityError as e: 
        raise UserExistsException


def get_outer_postcode(postcode):
    # Removing any whitespace and converting to uppercase:
    postcode = postcode.replace(" ", "").upper()
    
    # Regular expression to validate full postcode and extract outer postcode:
    # ^ Asserts the position at the start of the string.
    # ([A-Z]{1,2}\d[A-Z\d]?) Captures the outer postcode part:
    #     [A-Z]{1,2} Matches 1 or 2 uppercase letters.
    #     \d Matches a single digit.
    #     [A-Z\d]? Matches an optional uppercase letter or digit.
    # \d Matches a single digit (the start of the inward code).
    # [A-Z]{2} Matches exactly 2 uppercase letters (the rest of the inward code).
    # $ Asserts the position at the end of the string.
    full_postcode_regex = re.compile(r"^([A-Z]{1,2}\d[A-Z\d]?)\d[A-Z]{2}$")

    # Regular expression to validate outer postcode:
    # ^ Asserts the position at the start of the string.
    # [A-Z]{1,2} Matches 1 or 2 uppercase letters.
    # \d Matches a single digit.
    # [A-Z\d]? Matches an optional uppercase letter or digit.
    # $ Asserts the position at the end of the string.
    outer_postcode_regex = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?$")
    
    # If a full postcode has been provided, extracting the outer postcode:
    match = full_postcode_regex.match(postcode)
    if match:
        return match.group(1)
    
    # If an outer postcode has been provided, returning it:
    if outer_postcode_regex.match(postcode):
        return postcode

    # If the postcode is invalid, raising an exception:
    raise InvalidPostcodeException

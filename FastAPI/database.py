import os
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from strings import *


# Environment variable for the database URI:
DB_URI = os.getenv("DB_URI")

# Declaring the engine to connect with the DB:
engine = create_engine(DB_URI)

# sessionmaker class is used to create session objects to connect & interact with the DB:
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# declarative_base function is used to create a base class for all data models:
Base = declarative_base()


def create_system_message(db: Session, message: str, user_id=None) -> None:
    # Importing here to avoid circular imports:
    from models import Message, MessageType

    system_message = Message(user_id=user_id, type=MessageType.SYSTEM, text=message)
    db.add(system_message)
    db.commit()


def create_initial_system_messages(db: Session, messages: List[str]) -> None:
    # Importing here to avoid circular imports:
    from models import Message, MessageType

    # If system messages don't already exist, inserting them:
    existing_message = db.query(Message).filter_by(type=MessageType.SYSTEM, user_id=None).first()

    # Only inserting if there are no existing system messages:
    if not existing_message:
        for message in messages: create_system_message(db, message)
        

def db_setup() -> None:
    # Creating all the tables (if they don't already exist):
    Base.metadata.create_all(engine)

    # Creating a new session to connect to the DB using the session factory:
    db = SessionLocal()
    try:
        # Creating system messages:
        create_initial_system_messages(db, [ASSISTANT_CONTEXT])
    except Exception as e:
        db.rollback()
        print(f"Error during database setup: {e}")
    finally:
        db.close()

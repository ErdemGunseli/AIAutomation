import os
import base64
import requests
import json
from io import BytesIO
from typing import List, Optional


from services.assistant_service import completion
from llm_functions import function_schemas, call_function
from exceptions import AutomationNotFoundException
from dependencies import db_dependency, user_dependency, get_user
from database import SessionLocal
from models import Automation, AutomationLog


def get_automation(db: db_dependency, user: user_dependency, automation_id: int) -> Automation:
    automation = db.query(Automation).filter_by(id=automation_id, user_id=user.id).first()
    if not automation: raise AutomationNotFoundException
    return automation


def get_automations(db: db_dependency, user: user_dependency) -> List[Automation]:
    return db.query(Automation).filter_by(user_id=user.id).all()


def update_automation_activity(db: db_dependency, user: user_dependency, automation_id: int, active: bool) -> Automation:
    automation = get_automation(db, user, automation_id)
    automation.is_active = active
    db.commit()
    db.refresh(automation)
    return automation


def delete_automation(db: db_dependency, user: user_dependency, automation_id: int) -> None:
    automation = get_automation(db, user, automation_id)
    db.delete(automation)
    db.commit()


def get_automation_logs(db: db_dependency, user: user_dependency) -> List[AutomationLog]:
    # Returning all automation logs of automations associated to the user, newest log first:
    return db.query(AutomationLog).join(Automation).filter(Automation.user_id == user.id).order_by(AutomationLog.timestamp.desc()).all()


# Create framework to call this function when the interval time passes for each automation:
def evaluate_automation(automation_id: int) -> dict:
    # Not using dependency injection here, as this function is not run from an endpoint:
    db = SessionLocal()

    automation = db.query(Automation).filter_by(id=automation_id).first()
    if not automation: raise AutomationNotFoundException
    
    user = get_user(db, automation.user_id)

    try: 

        # Getting the function schema from the description:
        schema = json.loads(automation.description)
        print(schema)

        # Calling the assistant with the function schema:
        response = completion(db, user, 
            text=f"Evaluate automation, execute relevant action if conditions met: {schema}",
            save_messages=False)
        print(response)
          
    except Exception  as e:
        print(f"Error during automation execution: {e}")
        db.rollback()

    finally:
        db.close()


"""
There needs to be a system that gives the automation info to the assistant the next time that it needs to be checked.
The assistant can then utilise the description to call the necessary functions to check if the automation should be ran, and actually run it if it should be ran.
"""
from database import SessionLocal
from models import Automation, AutomationLog
from enums import AutomationResult


def create_automation(args: dict) -> dict:
    user_id = args.get("user_id")
    name = args.get("name")
    description = args.get("description")
    check_interval = args.get("check_interval")

    # Not using dependency injection here, as this function is not run from an endpoint:
    db = SessionLocal()
    try: 
        automation = Automation(
            user_id=user_id, 
            name=name, 
            description=description, 
            check_interval=check_interval
        )

        db.add(automation)
        db.commit()
        db.refresh(automation)

        return {"success": f"Automation '{name}' created successfully, with ID {automation.id}."}

    except Exception as e:
        db.rollback()
        raise e
    
    finally:
        db.close()


def create_automation_log(args: dict) -> dict:
    automation_id = args.get("automation_id")
    result = args.get("result").lower()
    description = args.get("description")

    print(f"RESULT: {result}")

    # Not using dependency injection here, as this function is not run from an endpoint:
    db = SessionLocal()
    try: 
        enum_result = AutomationResult(result)

        automation_log = AutomationLog(automation_id=automation_id, description=description, result=enum_result)

        db.add(automation_log)
        db.commit()
        db.refresh(automation_log)
        return {"success": f"Automation log created successfully, with ID {automation_log.id}."}

    except Exception as e:
        db.rollback()
        raise e    
    
    finally:
        db.close()


function_names = {"create_automation": create_automation, "create_automation_log": create_automation_log}


function_schemas = [
    {
        "type": "function", 
        "function": {
            "name": "create_automation",
            "description": "Creates a new automation for the user. The user needs to accept it for it to activate - remind this to the user.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "user_id": {
                        "type": "integer", 
                        "description": "The ID of the user who the automation is for, e.g. 6",        
                    },
                    "name": {
                        "type": "string", 
                        "description": "The name of the automation that concisely describes its purpose, e.g. Adjust Thermostat Based on Weather",        
                    },
                    "description": {
                        "type": "string", 
                        "description": "The description of the automation, including which functions to run and under which conditions.",        
                    },
                     "check_interval": {
                        "type": "string", 
                        "description": "Time in seconds between each check of the automation condition, e.g. 3600",        
                    },
                },
            "required": ["user_id", "name", "description", "check_interval"],
            },
        }
    },
   {
        "type": "function", 
        "function": {
            "name": "create_automation_log",
            "description": "Must be run when an automation is run/executed/evaluated. Creates a log, indicating the result of the automation check and additional info.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "automation_id": {
                        "type": "integer", 
                        "description": "The ID of the automation that was checked, e.g. 6",        
                    },
                    "result": {
                        "type": "string", 
                        "description": "The result of the automation check, that can ONLY take the values 'executed' (if conditions passed and an action was taken), 'not_executed' (if conditions weren't met), or 'fail' (if there was a problem).",        
                    },
                    "description": {
                        "type": "string", 
                        "description": "Include any relevant information about the automation run, such as what real-time data values were, which functions were executed and which weren't, or anything else that the automation description said to include.",        
                    },
                },
            "required": ["automation_id", "result"],
            },
        }
  }
]



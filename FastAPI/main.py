from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from dotenv import load_dotenv

# Loading environment variables and declaring FastAPI instance (before local imports):
load_dotenv()
app = FastAPI()

# Rate limiting with SlowAPI:
limiter = Limiter(key_func=get_remote_address, default_limits=["3/second", "120/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from routers import assistant, auth, automation, users
from config import read_config
from database import db_setup

# Creating the DB and inserting initial data:
db_setup()

# Including routers:
app.include_router(assistant.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(automation.router)


# Adding client domains to avoid CORS blocking:
origins = read_config("cors_origins")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, 
                   allow_methods=['*'], allow_headers=['*'])

"""
MANUAL QUERY NOT WORKING - ANY DB CONNECTIONS OPEN?
CREATE ABILITY TO READ ALL AUTOMATIONS TO DETERMINE IF ANOTHER ONE IS NECESSARY

Improve Assistant Prompt - ENSURE ASSISTANT ALWAYS LOGS

Implement pump manufacturer API and integrate it with the assistant
Implement smart meter API and integrate with the assistant

Create system to manually trigger automations


CHATGPT FULL CODE REVIEW

CREATE CODE SUMMARY FOR TECHNICAL PEOPLE (BUT NOT NECESSARILY WEB DEVS)

DIAGRAM FOR ASSISTANT INTERACTION
"""


"""
Run the backend:
cd FastAPI
uvicorn main:app --reload

If virtual environment inactive:
cd FastAPI
source venv/bin/activate
uvicorn main:app --reload
"""

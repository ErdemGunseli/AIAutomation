from typing import List

from fastapi import APIRouter, status as st, Path
from starlette.requests import Request

from main import app
from dependencies import db_dependency, user_dependency
from schemas import AutomationResponse, AutomationLogResponse
from services import automation_service


router = APIRouter(prefix="/automations", tags=["Automations"])


@router.get("/{automation_id}", response_model=AutomationResponse, status_code=st.HTTP_200_OK)
@app.state.limiter.limit("")
async def read_automation(db: db_dependency, user: user_dependency, request: Request, automation_id: int = Path(ge=0)):
    return automation_service.get_automation(db, user, automation_id)


@router.put("/{automation_id}/activity/{active}", response_model=AutomationResponse, status_code=st.HTTP_200_OK)
@app.state.limiter.limit("")
async def update_automation_activity(db: db_dependency, user: user_dependency, request: Request, automation_id: int = Path(ge=0), active: bool = Path(...)):
    return automation_service.update_automation_activity(db, user, automation_id, active)


@router.delete("/{automation_id}", response_model=AutomationResponse, status_code=st.HTTP_200_OK)
@app.state.limiter.limit("")
async def delete_automation(db: db_dependency, user: user_dependency, request: Request, automation_id: int = Path(ge=0)):
    return automation_service.delete_automation(db, user, automation_id)


@router.get("/", response_model=List[AutomationResponse], status_code=st.HTTP_200_OK)
@app.state.limiter.limit("")
async def read_automations(db: db_dependency, user: user_dependency, request: Request):
    return automation_service.get_automations(db, user)


@router.get("/{automation_id}/logs", response_model=List[AutomationLogResponse], status_code=st.HTTP_200_OK)
@app.state.limiter.limit("")
async def read_automation_logs(db: db_dependency, user: user_dependency, request: Request):
    return automation_service.get_automation_logs(db, user)
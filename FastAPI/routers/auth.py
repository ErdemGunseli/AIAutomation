from fastapi import APIRouter, status as st
from starlette.requests import Request

from main import app
from dependencies import db_dependency, auth_dependency
from schemas import TokenResponse
from services import auth_service as aus


router = APIRouter(prefix="/auth", tags=["User Authentication"])


@router.post("/token", response_model=TokenResponse, status_code=st.HTTP_200_OK)
@app.state.limiter.limit("")
async def login_and_generate_token(db: db_dependency, auth_form: auth_dependency, request: Request):
    return aus.login_and_generate_token(db, auth_form)
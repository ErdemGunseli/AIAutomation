from fastapi import APIRouter, status as st
from starlette.requests import Request

from main import app
from services import user_service as us
from schemas import CreateUserRequest, UserResponse
from dependencies import user_dependency, db_dependency


router = APIRouter(prefix="/user", tags=["User"])


@router.post("/", response_model=UserResponse, status_code=st.HTTP_201_CREATED)
@app.state.limiter.limit("")
async def create_user(db: db_dependency, user_data: CreateUserRequest, request: Request):
    return us.create_user(db, user_data)


@router.get("/", response_model=UserResponse, status_code=st.HTTP_200_OK)
@app.state.limiter.limit("")
async def read_current_user(user: user_dependency, request: Request):
    return user

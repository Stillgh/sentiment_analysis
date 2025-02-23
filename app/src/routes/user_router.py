from fastapi import APIRouter, Depends, HTTPException, Form, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlmodel import Session
from typing import Annotated

from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse

from config.auth_config import get_auth_settings
from database.database import get_session
from entities.auth.auth_entities import TokenData
from entities.user.user import UserSignUp, UserDTO
from routes.home_router import templates
from service.auth.auth_service import get_current_active_user, authenticate_cookie
from service.auth.jwt_service import create_access_token
from service.crud.user_service import (
    create_user,
    add_balance,
    withdraw_balance,
    get_balance_histories, get_user_by_email, find_and_verify_user
)
from service.mappers.user_mapper import user_signup_dto_to_user

user_router = APIRouter(prefix="/users", tags=["User"])


@user_router.post("/login")
async def login(
        user_login: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
) -> RedirectResponse:
    auth_settings = get_auth_settings()
    user = find_and_verify_user(user_login.username, user_login.password, session)
    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=auth_settings.COOKIE_NAME,
        value=f"Bearer {create_access_token(user)}",
        httponly=True
    )
    return response


@user_router.post("/token")
async def get_token(
        user_login: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
) -> dict:
    auth_settings = get_auth_settings()
    user = find_and_verify_user(user_login.username, user_login.password, session)

    return {auth_settings.COOKIE_NAME: create_access_token(user), "token_type": "bearer"}


@user_router.post("/signup")
async def create_new_user(
        username: str = Form(...),
        surname: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        session: Session = Depends(get_session)) -> RedirectResponse:
    user_data = UserSignUp(name=username, surname=surname, email=email, password=password)
    user = get_user_by_email(user_data.email, session)
    auth_settings = get_auth_settings()
    if user:
        raise HTTPException(status_code=409, detail=f"User with email {user_data.email}  already exists")
    try:
        user = user_signup_dto_to_user(user_data)
        create_user(user, session)
        response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)

        response.set_cookie(
            key=auth_settings.COOKIE_NAME,
            value=f"Bearer {create_access_token(user)}",
            httponly=True
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.post("/balance/add")
async def add_user_balance(
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session),
        amount: float = Body(..., embed=True)
) -> dict:
    try:
        user = await get_current_active_user(token, session)
        add_balance(user.email, amount, session)
        return {
            "message": f"Successfully added {amount} to balance for user {user.email}",
            "new_balance": float(user.balance)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.post("/balance/withdraw")
async def withdraw_user_balance(
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session),
        amount: float = Body(..., embed=True)
):
    try:
        user = await get_current_active_user(token, session)
        withdraw_balance(user.id, amount, session)
        return {
            "message": f"Successfully withdrew {amount} from balance for user {user.email}",
            "new_balance": float(user.balance)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.get("/balance/current", response_model=float)
async def get_user_current_balance(
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session)
):
    user = await get_current_active_user(token, session)

    return user.balance


@user_router.get("/balance/history", response_class=HTMLResponse)
async def balance_history(
        request: Request,
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session)
):
    user = await get_current_active_user(token, session)
    history = get_balance_histories(user.id, session)
    return templates.TemplateResponse("balance_history.html", {"request": request, "history": history})


@user_router.get("/myinfo", response_model=UserDTO)
async def my_info(
        request: Request,
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session)
):
    user = await get_current_active_user(token, session)
    return templates.TemplateResponse("myinfo.html", {"request": request, "user": user})



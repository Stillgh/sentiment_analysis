from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Annotated

from config.auth_config import get_auth_settings
from database.database import get_session
from entities.auth.auth_entities import Token, TokenData
from entities.task.prediction_task import PredictionTask
from entities.user.user import User, UserSignUp, UserLogin, UserDTO
from entities.user.balance_history import BalanceHistory
from service.auth.auth_service import create_access_token, get_current_active_user, verify_token
from service.crud.model_service import get_prediction_histories_by_user
from service.crud.user_service import (
    get_all_users,
    create_user,
    add_balance,
    withdraw_balance,
    get_balance_histories, get_user_by_email, verify_password
)
from service.mappers.user_mapper import user_to_user_dto, user_signup_dto_to_user

user_router = APIRouter(prefix="/users", tags=["User"])
auth_config = get_auth_settings()


@user_router.get("/all", response_model=List[UserDTO])
async def get_users(
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: Session = Depends(get_session)):
    return map(user_to_user_dto, get_all_users(session))


@user_router.post("/login")
async def login_for_access_token(
        user_login: UserLogin,
        session: Session = Depends(get_session)
) -> Token:
    user = get_user_by_email(user_login.email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=409, detail="Password mismatch")

    access_token_expires = timedelta(minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, secret_key=auth_config.SECRET_KEY, algorithm=auth_config.ALGORITHM,
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@user_router.post("/signup")
async def create_new_user(user_data: UserSignUp, session: Session = Depends(get_session)) -> dict:
    user = get_user_by_email(user_data.email, session)
    if user:
        raise HTTPException(status_code=409, detail=f"User with email {user_data.email}  already exists")
    try:
        create_user(user_signup_dto_to_user(user_data), session)
        return {"message": "User successfully registered!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.post("/balance/add")
async def add_user_balance(
        amount: float,
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: Session = Depends(get_session)
) -> dict:
    try:
        add_balance(current_user.email, amount, session)
        return {"message": f"Successfully added {amount} to balance for user {current_user.email}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.post("/balance/withdraw")
async def withdraw_user_balance(
        amount: float,
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: Session = Depends(get_session)
):
    try:
        withdraw_balance(current_user.email, amount, session)
        return {"message": f"Successfully withdrew {amount} from balance for user {current_user.email}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.get("/balance/current", response_model=dict)
async def get_user_current_balance(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return {"message": f"User {current_user.email} balance is {current_user.balance}"}


@user_router.get("/balance/history", response_model=List[BalanceHistory])
async def get_user_balance_history(
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: Session = Depends(get_session)
):
    return get_balance_histories(current_user.id, session)


@user_router.get("/predictions", response_model=List[PredictionTask])
async def get_user_prediction_history(
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: Session = Depends(get_session)
):

    predictions = get_prediction_histories_by_user(current_user.id, session)
    return predictions


@user_router.get("/myinfo", response_model=UserDTO)
async def my_info(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

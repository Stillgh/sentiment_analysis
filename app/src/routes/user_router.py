from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List


from database.database import get_session
from entities.task.prediction_task import PredictionTask
from entities.user.user import User, UserSignUp, UserLogin, UserDTO
from entities.user.balance_history import BalanceHistory
from service.crud.model_service import get_prediction_histories_by_user
from service.crud.user_service import (
    get_all_users,
    create_user,
    add_balance,
    withdraw_balance,
    get_balance_histories, get_user_by_email, hash_password, verify_password
)
from service.mappers.user_mapper import user_to_user_dto, user_signup_dto_to_user

user_router = APIRouter(prefix="/users", tags=["User"])


@user_router.get("/all", response_model=List[UserDTO])
async def get_users(session: Session = Depends(get_session)):
    return map(user_to_user_dto, get_all_users(session))


@user_router.post("/login")
async def login(user_login: UserLogin, session: Session = Depends(get_session)) -> dict:
    user = get_user_by_email(user_login.email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=409, detail="Password mismatch")
    return {"message": "User signed in successfully!"}


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


@user_router.post("/{email}/balance/add")
async def add_user_balance(
        email: str,
        amount: float,
        session: Session = Depends(get_session)
) -> dict:
    try:
        add_balance(email, amount, session)
        return {"message": f"Successfully added {amount} to balance for user {email}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.post("/{email}/balance/withdraw")
async def withdraw_user_balance(
        email: str,
        amount: float,
        session: Session = Depends(get_session)
):
    try:
        withdraw_balance(email, amount, session)
        return {"message": f"Successfully withdrew {amount} from balance for user {email}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.get("/{email}/balance/current", response_model=dict)
async def get_user_current_balance(
        email: str,
        session: Session = Depends(get_session)
):
    user = get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {email} balance is {user.balance}"}


@user_router.get("/{email}/balance/history", response_model=List[BalanceHistory])
async def get_user_balance_history(
        email: str,
        session: Session = Depends(get_session)
):
    user = get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_balance_histories(user.id, session)


@user_router.get("/{email}/predictions", response_model=List[PredictionTask])
async def get_user_prediction_history(
        email: str,
        session: Session = Depends(get_session)
):
    user = get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    predictions = get_prediction_histories_by_user(user.id, session)
    return predictions

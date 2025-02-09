import os
import uuid
from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlmodel import Session

from config.auth_config import get_auth_settings
from database.database import get_session
from entities.auth.auth_entities import TokenData
from service.crud.user_service import get_user_by_email, get_user_by_id
from service.mappers.user_mapper import user_to_user_dto

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

auth_config = get_auth_settings()


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str, session: Session):
    user = get_user_by_email(email, session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, secret_key: str, algorithm: str, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


async def verify_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth_config.SECRET_KEY, algorithms=[auth_config.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(username=user_id)
    except InvalidTokenError:
        raise credentials_exception
    return token_data


async def get_current_active_user(
        token_data: Annotated[TokenData, Depends(verify_token)], session: Annotated[Session, Depends(get_session)],
):
    current_user = get_user_by_id(uuid.UUID(token_data.username), session)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user_to_user_dto(current_user)

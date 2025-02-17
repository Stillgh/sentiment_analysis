from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlmodel import Session

from entities.auth.auth_entities import TokenData, OAuth2PasswordBearerWithCookie
from service.auth.jwt_service import verify_token, oauth2_scheme
from service.crud.user_service import get_user_by_email, get_user_by_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme_cookie = OAuth2PasswordBearerWithCookie(tokenUrl="/users/token")


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


async def get_current_active_user(
        token_data: TokenData, session: Session
):
    current_user = get_user_by_id(token_data.user_id, session)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def authenticate(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access"
        )
    decoded_token = verify_token(token)
    return decoded_token.username


async def authenticate_cookie(token: str = Depends(oauth2_scheme_cookie)) -> TokenData:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access"
        )
    token = token.removeprefix('Bearer ')
    decoded_token = verify_token(token)
    return decoded_token

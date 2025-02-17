from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse

from config.auth_config import get_auth_settings
from database.database import get_session
from entities.auth.auth_entities import TokenData
from entities.user.user_role import UserRole
from routes.home_router import templates
from service.auth.auth_service import authenticate_cookie, get_current_active_user
from service.crud.user_service import get_all_users
from service.mappers.user_mapper import user_to_user_dto

admin_router = APIRouter(prefix="/admin", tags=["Admin"])
auth_config = get_auth_settings()


@admin_router.get("/", response_class=HTMLResponse)
async def admin_panel(
        request: Request,
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session)
):
    admin_user = await get_current_active_user(token, session)
    if admin_user.role != UserRole.ADMIN:
        return templates.TemplateResponse("admin_required.html", {"request": request})
    return templates.TemplateResponse("admin.html", {"request": request})


@admin_router.get("/users", response_class=HTMLResponse)
async def get_users(
        request: Request,
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session)):
    user = await get_current_active_user(token, session)

    if not user or user.role != UserRole.ADMIN:
        return templates.TemplateResponse("admin_required.html", {"request": request})
    all_users = list(map(user_to_user_dto, get_all_users(session)))
    return templates.TemplateResponse("admin_users.html", {"request": request, "users": all_users})


@admin_router.get("/admin_required", response_class=HTMLResponse)
async def admin_required(request: Request,
                         token: Annotated[TokenData, Depends(authenticate_cookie)],
                         session: Annotated[Session, Depends(get_session)]):
    user = await get_current_active_user(token, session)
    if not user or user.role != UserRole.ADMIN:
        return templates.TemplateResponse("admin_required.html", {"request": request})
    return templates.TemplateResponse("admin.html", {"request": request})

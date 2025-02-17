from fastapi import APIRouter, Depends
from jwt import InvalidTokenError
from sqlmodel import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from config.auth_config import get_auth_settings
from database.database import get_session
from entities.auth.auth_entities import TokenData
from service.auth.auth_service import authenticate_cookie, get_current_active_user

settings = get_auth_settings()
home_router = APIRouter(tags=["Home"])
templates = Jinja2Templates(directory="src/templates")


@home_router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    token = request.cookies.get(settings.COOKIE_NAME)
    try:
        if token:
            user = await authenticate_cookie(token)
        else:
            user = None
    except InvalidTokenError as e:
        user = None

    context = {
        "user": user.username if user else "",
        "request": request
    }
    return templates.TemplateResponse("index.html", context)


@home_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@home_router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@home_router.get("/home", response_class=HTMLResponse)
async def home_page(
        request: Request,
        token: TokenData = Depends(authenticate_cookie),
        session: Session = Depends(get_session)
):
    user = await get_current_active_user(token, session)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})


@home_router.get("/logout", response_class=HTMLResponse)
async def login_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response

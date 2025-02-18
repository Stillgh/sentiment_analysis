import os
import threading

from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse

from database.database import get_session
from database.tables_initiator import init_db
from entities.auth.auth_entities import settings
from routes.admin_router import admin_router
from routes.prediction_router import prediction_router
from routes.user_router import user_router
from routes.home_router import home_router
from service.auth.auth_service import get_current_active_user
from service.auth.jwt_service import verify_token
from tg_api.tg_api import TgBot

app = FastAPI()
tg_bot = TgBot()

app.include_router(user_router)
app.include_router(home_router)
app.include_router(prediction_router)
app.include_router(admin_router)

ALLOWED_PATHS = ["/", "/login", "/signup", "/users/signup", "/users/login"]


@app.middleware("http")
async def restrict_access_middleware(request: Request, call_next):
    if request.url.path not in ALLOWED_PATHS:
        token = request.cookies.get(settings.COOKIE_NAME)
        try:
            if not token:
                return RedirectResponse(url="/")
            token_data = verify_token(token)
            user = await get_current_active_user(token_data, next(get_session()))
            if not user:
                response = RedirectResponse(url="/")
                response.delete_cookie(key=settings.COOKIE_NAME)
                return response
        except Exception as e:
            response = RedirectResponse(url="/")
            response.delete_cookie(key=settings.COOKIE_NAME)
            return response
    response = await call_next(request)
    return response


@app.on_event("startup")
def on_startup():
    load_dotenv()
    init_db()
    tg_bot.setup()
    bot_thread = threading.Thread(target=tg_bot.start_polling, daemon=True)
    bot_thread.start()


if __name__ == "__main__":
    HOST = os.getenv('APP_HOST')
    PORT = int(os.getenv('APP_PORT'))

    uvicorn.run('main:app', host=HOST, port=PORT, reload=True)

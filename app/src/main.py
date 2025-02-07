import os
import threading

from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI

from database.database import init_db
from routes.prediction_router import prediction_router
from routes.user_router import user_router
from routes.home_router import home_router
from tg_api.tg_api import TgBot

app = FastAPI()
tg_bot = TgBot()

app.include_router(user_router)
app.include_router(home_router)
app.include_router(prediction_router)


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

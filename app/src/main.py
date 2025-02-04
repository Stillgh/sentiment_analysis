import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI

load_dotenv()

HOST = os.getenv('APP_HOST')
PORT = int(os.getenv('APP_PORT'))

app = FastAPI()


@app.get('/')
async def hello_world() -> str:
    return 'Hello World!'


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)

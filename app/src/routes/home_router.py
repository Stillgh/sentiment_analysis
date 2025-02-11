from fastapi import APIRouter

home_router = APIRouter(tags=["Home"])


@home_router.get('/')
async def index() -> str:
    return "Hello World!"

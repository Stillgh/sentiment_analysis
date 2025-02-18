import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from celery_worker import perform_prediction
from database.database import get_session
from entities.auth.auth_entities import TokenData
from entities.task.prediction_request import PredictionRequest
from entities.task.prediction_task import PredictionTask, PredictionDTO
from routes.home_router import templates
from service.auth.auth_service import get_current_active_user, authenticate_cookie
from service.crud.model_service import get_model_by_name, get_default_model, get_all_prediction_history, validate_input, \
    get_prediction_task_by_id, get_model_by_id, get_prediction_histories_by_user
from service.mappers.prediction_mapper import prediction_task_to_dto

prediction_router = APIRouter(prefix="/prediction", tags=["Prediction"])
custom_executor = ThreadPoolExecutor(max_workers=20)


@prediction_router.post("/predict")
async def create_prediction(
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session),
        inference_input: str = Body(..., embed=True),
        model_name: str = Body(..., embed=True),

):
    if not validate_input(inference_input):
        raise HTTPException(status_code=400, detail="Input len should be > 5")

    model = get_model_by_name(model_name, session) if model_name else get_default_model(session)
    if not model:
        model = get_default_model(session)
    user = await get_current_active_user(token, session)

    if user.balance < model.prediction_cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Required: {model.prediction_cost}, Available: {user.balance}"
        )

    prediction_request = PredictionRequest(
        user_id=user.id,
        model_id=model.id,
        inference_input=inference_input,
        user_balance_before_task=user.balance,
        request_timestamp=datetime.now()
    )
    task_id = uuid.uuid4()
    try:
        perform_prediction.delay(prediction_request.dict(), task_id, model.name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Task error: {exc}")

    return {"task_id": task_id}


@prediction_router.post("/prediction_result", response_model=PredictionDTO)
async def get_prediction(
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session),
        task_id: uuid.UUID = Body(..., embed=True)
):
    user = await get_current_active_user(token, session)
    task = get_prediction_task_by_id(task_id, session)
    if not task:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"detail": "Prediction task is still processing. Please try again later."}
        )
    return prediction_task_to_dto(task, user.email, get_model_by_id(task.model_id, session).name)


@prediction_router.get("/history", response_class=HTMLResponse)
async def show_prediction_history(
        request: Request,
        token: Annotated[TokenData, Depends(authenticate_cookie)],
        session: Session = Depends(get_session)
):
    user = await get_current_active_user(token, session)
    predictions = get_prediction_histories_by_user(user.id, session)
    prediction_dtos = [
        prediction_task_to_dto(task, user.email, get_model_by_id(task.model_id, session).name)
        for task in predictions
    ]
    return templates.TemplateResponse("prediction_history.html", {"request": request, "predictions": prediction_dtos})


@prediction_router.get("/all", response_model=List[PredictionTask])
async def get_prediction_history(
        session: Session = Depends(get_session)
):
    return get_all_prediction_history(session)

import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from celery_worker import perform_prediction
from database.database import get_session
from entities.task.prediction_request import PredictionRequest
from entities.task.prediction_task import PredictionTask, PredictionDTO
from entities.user.user import User
from service.auth.auth_service import get_current_active_user
from service.crud.model_service import get_model_by_name, get_default_model, get_all_prediction_history, validate_input, \
    get_prediction_task_by_id, get_model_by_id
from service.mappers.prediction_mapper import prediction_task_to_dto

prediction_router = APIRouter(prefix="/prediction", tags=["Prediction"])
custom_executor = ThreadPoolExecutor(max_workers=20)


@prediction_router.post("/predict")
async def create_prediction(
        inference_input: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        model_name: str | None = None,
        session: Session = Depends(get_session)
):
    if not validate_input(inference_input):
        raise HTTPException(status_code=400, detail="Input len should be > 2")

    model = get_model_by_name(model_name, session) if model_name else get_default_model()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    print(f'User bal {current_user.balance} model cost {model.prediction_cost}')
    if current_user.balance < model.prediction_cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Required: {model.prediction_cost}, Available: {current_user.balance}"
        )

    prediction_request = PredictionRequest(
        user_id=current_user.id,
        model_id=model.id,
        inference_input=inference_input,
        user_balance_before_task=current_user.balance,
        request_timestamp=datetime.now()
    )
    task_id = uuid.uuid4()
    try:
        perform_prediction.delay(prediction_request.dict(), task_id, model.name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Task error: {exc}")

    return f"Task is running, task id is {task_id}. Check result at /prediction_result"


@prediction_router.post("/prediction_result", response_model=PredictionDTO)
async def create_prediction(
        task_id: uuid.UUID,
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: Session = Depends(get_session)
):
    task = get_prediction_task_by_id(task_id, session)
    if not task:
        return f"Task with id: {task_id} is not ready yet"
    return prediction_task_to_dto(task, current_user.email, get_model_by_id(task.model_id, session).name)


@prediction_router.get("/all", response_model=List[PredictionTask])
async def get_prediction_history(
        session: Session = Depends(get_session)
):
    return get_all_prediction_history(session)

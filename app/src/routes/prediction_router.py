import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Annotated, List
from celery.exceptions import TimeoutError as CeleryTimeoutError

from celery import chain
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from celery_worker import validate_request, perform_prediction
from database.database import get_session
from entities.task.prediction_request import PredictionRequest
from entities.task.prediction_task import PredictionDTO, PredictionTask
from entities.user.user import User
from service.auth.auth_service import get_current_active_user
from service.crud.model_service import get_model_by_name, get_default_model, get_all_prediction_history
from service.crud.user_service import withdraw_balance
from service.mappers.prediction_mapper import prediction_task_to_dto

prediction_router = APIRouter(prefix="/prediction", tags=["Prediction"])
custom_executor = ThreadPoolExecutor(max_workers=20)


@prediction_router.post("/predict", response_model=PredictionDTO)
async def create_prediction(
        inference_input: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        model_name: str | None = None,
        session: Session = Depends(get_session)
):
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

    task_chain = chain(
        validate_request.s(prediction_request.dict()),
        perform_prediction.s(model.name)
    )

    async_result = task_chain()

    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(custom_executor, async_result.get, 10)
    except CeleryTimeoutError:
        raise HTTPException(
            status_code=202,
            detail=f"Task is still processing. You can retrieve the result later calling /prediction/all."
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Task error: {exc}")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    result = PredictionTask(**result)
    if result.is_success:
        withdraw_balance(current_user.email, model.prediction_cost, session)
        print('Balance withdrawed')
    return prediction_task_to_dto(result, current_user.email, model_name)


@prediction_router.get("/all", response_model=List[PredictionTask])
async def get_prediction_history(
        session: Session = Depends(get_session)
):
    return get_all_prediction_history(session)

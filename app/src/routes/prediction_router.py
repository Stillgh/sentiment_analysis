from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from database.database import get_session
from entities.task.prediction_request import PredictionRequest
from entities.task.prediction_task import PredictionTask, PredictionDTO
from service.crud.model_service import get_model_by_name, get_default_model, make_prediction
from service.crud.user_service import get_user_by_email, withdraw_balance
from service.mappers.prediction_mapper import prediction_task_to_dto

prediction_router = APIRouter(prefix="/prediction", tags=["Prediction"])


@prediction_router.post("/predict", response_model=PredictionDTO)
async def create_prediction(
    email: str,
    inference_input: str,
    model_name: str | None = None,
    session: Session = Depends(get_session)
):
    user = get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    model = get_model_by_name(model_name, session) if model_name else get_default_model()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    print(f'User bal {user.balance} model cost {model.prediction_cost}')
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
    print('Received prediction request')
    task = make_prediction(prediction_request, model, session)
    print(f'Predicted result, success: {task.is_success}')
    if task.is_success:
        withdraw_balance(user.email, model.prediction_cost, session)
        print('Balance withdrawed')
    return prediction_task_to_dto(task, email, model_name)

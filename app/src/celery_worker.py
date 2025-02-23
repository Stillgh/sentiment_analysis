import os
import uuid

from celery import Celery

from database.database import get_session
from entities.ml_model.inference_input import InferenceInput
from entities.task.prediction_request import PredictionRequest
from exceptions.model_exception import ModelException
from service.crud.model_service import get_model_by_name, prepare_and_save_task, make_prediction
from service.crud.user_service import withdraw_balance

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")


@celery.task(queue='prediction')
def perform_prediction(prediction_request: dict, task_id: uuid, model_name: str) -> dict:
    print("Starting prediction")

    model = get_model_by_name(model_name, next(get_session()))

    try:
        result = make_prediction(model, InferenceInput(prediction_request['inference_input']))
        prepare_and_save_task(PredictionRequest(**prediction_request), result, True, model.prediction_cost, task_id, next(get_session()))
        withdraw_balance(prediction_request['user_id'], model.prediction_cost, next(get_session()))
        return "Prediction succeeded"

    except Exception as exc:
        error_mes = f"Error during model prediction {exc}"
        prepare_and_save_task(PredictionRequest(**prediction_request), error_mes, False, 0, task_id, next(get_session()))
        raise ModelException(error_mes, 500)



import os

from celery import Celery

from database.database import get_session
from entities.ml_model.classification_model import ClassificationModel
from entities.user import user
from entities.ml_model import classification_model
from entities.task.prediction_request import PredictionRequest
from service.crud.model_service import make_prediction, get_default_model, get_model_by_name, save_failed_task

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")


@celery.task(queue='validation')
def validate_request(prediction_request: dict) -> dict:
    print("Starting validation")
    if not prediction_request['inference_input'] or len(prediction_request['inference_input']) < 2:
        print("Validation error")
        save_failed_task(PredictionRequest(**prediction_request), "Validation error. Len should be > 1", next(get_session()))
        raise ValueError("Invalid data: Len should be > 1")
    print("Validation succeeded")
    return prediction_request


@celery.task(queue='prediction')
def perform_prediction(prediction_request: dict, model_name: str) -> dict:
    print("Starting predictionStarting prediction")

    model = get_model_by_name(model_name, next(get_session())) if model_name else get_default_model()
    if not model:
        model = get_default_model()
    task = make_prediction(PredictionRequest(**prediction_request), model, next(get_session()))
    print("Prediction succeeded")
    return task.dict()

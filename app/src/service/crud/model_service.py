from datetime import datetime
import uuid
from typing import List

from sqlmodel import Session, select

from entities.task.prediction_request import PredictionRequest
from entities.task.prediction_result import PredictionResult
from entities.task.prediction_task import PredictionTask
from entities.ml_model.ml_model import MLModel

from entities.ml_model.classification_model import ClassificationModel


def create_model(new_model: ClassificationModel, session: Session) -> None:
    session.add(new_model)
    session.commit()
    session.refresh(new_model)


def get_all_models(session: Session) -> List[MLModel]:
    return session.query(ClassificationModel).all()


def make_prediction(prediction_requests: List[PredictionRequest], model: ClassificationModel, session: Session) -> List[
    PredictionTask]:
    results = [PredictionResult(
        result="[1]",
        is_success=True,
        balance_withdrawal=model.prediction_cost,
        result_timestamp=datetime.now()
    ) for _ in prediction_requests]
    tasks = []
    for req, res in zip(prediction_requests, results):
        task = PredictionTask(
            id=uuid.uuid4(),
            user_id=req.user_id,
            model_id=req.model_id,
            inference_input=req.inference_input,
            user_balance_before_task=req.user_balance_before_task,
            request_timestamp=req.request_timestamp,
            result=res.result,
            is_success=res.is_success,
            balance_withdrawal=res.balance_withdrawal,
            result_timestamp=res.result_timestamp
        )
        tasks.append(task)

    try:
        for task in tasks:
            session.add(task)
        session.commit()
        print("Created prediction tasks successfully!")
    except Exception as e:
        print(f"Error creating prediction tasks: {e}")
        session.rollback()

    return tasks


def get_all_prediction_history(session: Session) -> List[PredictionTask]:
    return session.query(PredictionTask).all()


def get_prediction_histories_by_user(user_id: uuid.UUID, session: Session) -> List[PredictionTask]:
    statement = select(PredictionTask) \
        .where(PredictionTask.user_id == user_id) \
        .order_by(PredictionTask.timestamp.desc())

    result = session.exec(statement).all()
    return result


def get_prediction_histories_by_model(model_id: uuid.UUID, session: Session) -> List[PredictionTask]:
    statement = select(PredictionTask) \
        .where(PredictionTask.model_id == model_id) \
        .order_by(PredictionTask.timestamp.desc())

    result = session.exec(statement).all()
    return result

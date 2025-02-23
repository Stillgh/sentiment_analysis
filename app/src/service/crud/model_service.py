from datetime import datetime
import uuid
from typing import List

from sqlmodel import Session, select, delete

from entities.ml_model.inference_input import InferenceInput
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


def get_model_by_id(id: uuid, session: Session) -> ClassificationModel:
    statement = select(ClassificationModel).where(ClassificationModel.id == id)
    result = session.exec(statement).first()
    return result


def create_and_save_default_model():
    return ClassificationModel(name='LogisticRegression', model_type='classification', prediction_cost=100.0)


def get_default_model(session: Session):
    return get_model_by_name('LogisticRegression', session)


def get_model_by_name(name: str, session: Session) -> ClassificationModel:
    statement = select(ClassificationModel) \
        .where(ClassificationModel.name == name)

    result = session.exec(statement).first()
    return result


def make_prediction(model: ClassificationModel, inference_input: InferenceInput) -> str:
    return "positive" if len(inference_input.data) > 10 else "neutral"
    # return model.predict(inference_input)


def prepare_and_save_task(request: PredictionRequest, result: str, is_success: bool, cost: float,
                          task_id: uuid, session: Session) -> PredictionTask:
    pred_result = PredictionResult(
        result=result,
        is_success=is_success,
        balance_withdrawal=cost,
        result_timestamp=datetime.now()
    )

    task = PredictionTask(
        id=task_id,
        user_id=request.user_id,
        model_id=request.model_id,
        inference_input=request.inference_input,
        user_balance_before_task=request.user_balance_before_task,
        request_timestamp=request.request_timestamp,
        result=pred_result.result,
        is_success=pred_result.is_success,
        balance_withdrawal=pred_result.balance_withdrawal,
        result_timestamp=pred_result.result_timestamp
    )
    task = save_task(task, session)
    return task


def save_task(task: PredictionTask, session: Session) -> PredictionTask:
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        print("Created prediction tasks successfully!")
    except Exception as e:
        print(f"Error creating prediction tasks: {e}")
        session.rollback()
    return task


def get_all_prediction_history(session: Session) -> List[PredictionTask]:
    return session.query(PredictionTask).all()


def get_prediction_task_by_id(task_id: uuid, session: Session) -> PredictionTask:
    statement = select(PredictionTask).where(PredictionTask.id == task_id)
    result = session.exec(statement).first()
    return result


def get_prediction_histories_by_user(user_id: uuid.UUID, session: Session) -> List[PredictionTask]:
    statement = select(PredictionTask) \
        .where(PredictionTask.user_id == user_id) \
        .order_by(PredictionTask.request_timestamp.desc())

    result = session.exec(statement).all()
    return result


def remove_prediction_histories_by_user(user_id: uuid.UUID, session: Session) -> int:
    statement = delete(PredictionTask).where(PredictionTask.user_id == user_id)
    result = session.exec(statement)
    session.commit()
    return result.rowcount

def get_prediction_histories_by_model(model_id: uuid.UUID, session: Session) -> List[PredictionTask]:
    statement = select(PredictionTask) \
        .where(PredictionTask.model_id == model_id) \
        .order_by(PredictionTask.request_timestamp.desc())

    result = session.exec(statement).all()
    return result


def validate_input(inference_input: str) -> bool:
    return inference_input is not None and len(inference_input) > 5

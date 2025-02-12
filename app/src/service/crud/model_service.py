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


def get_default_model():
    return ClassificationModel(name='LogisticRegression', model_type='classification', prediction_cost=100.0)


def get_model_by_name(name: str, session: Session) -> ClassificationModel:
    statement = select(ClassificationModel) \
        .where(ClassificationModel.name == name)

    result = session.exec(statement).first()
    return result


def save_failed_task(prediction_request: PredictionRequest, error_mes: str, session: Session):
    result = PredictionResult(
        result=error_mes,
        is_success=False,
        balance_withdrawal=0,
        result_timestamp=datetime.now()
    )
    task = PredictionTask(
        id=uuid.uuid4(),
        user_id=prediction_request.user_id,
        model_id=prediction_request.model_id,
        inference_input=prediction_request.inference_input,
        user_balance_before_task=prediction_request.user_balance_before_task,
        request_timestamp=prediction_request.request_timestamp,
        result=result.result,
        is_success=result.is_success,
        balance_withdrawal=result.balance_withdrawal,
        result_timestamp=result.result_timestamp
    )

    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        print("Saved failed prediction task")
    except Exception as e:
        print(f"Error creating prediction tasks: {e}")
        session.rollback()
    return task


def make_prediction(prediction_request: PredictionRequest, model: ClassificationModel,
                    session: Session) -> PredictionTask:
    result = PredictionResult(
        result="[1]",
        is_success=True,
        balance_withdrawal=model.prediction_cost,
        result_timestamp=datetime.now()
    )

    task = PredictionTask(
        id=uuid.uuid4(),
        user_id=prediction_request.user_id,
        model_id=prediction_request.model_id,
        inference_input=prediction_request.inference_input,
        user_balance_before_task=prediction_request.user_balance_before_task,
        request_timestamp=prediction_request.request_timestamp,
        result=result.result,
        is_success=result.is_success,
        balance_withdrawal=result.balance_withdrawal,
        result_timestamp=result.result_timestamp
    )

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


def get_prediction_histories_by_user(user_id: uuid.UUID, session: Session) -> List[PredictionTask]:
    statement = select(PredictionTask) \
        .where(PredictionTask.user_id == user_id) \
        .order_by(PredictionTask.request_timestamp.desc())

    result = session.exec(statement).all()
    return result


def get_prediction_histories_by_model(model_id: uuid.UUID, session: Session) -> List[PredictionTask]:
    statement = select(PredictionTask) \
        .where(PredictionTask.model_id == model_id) \
        .order_by(PredictionTask.timestamp.desc())

    result = session.exec(statement).all()
    return result

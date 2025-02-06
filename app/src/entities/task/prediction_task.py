import uuid

from sqlmodel import SQLModel, Field

from entities.task.prediction_request import PredictionRequest
from entities.task.prediction_result import PredictionResult


class PredictionTask(PredictionRequest, PredictionResult, SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)



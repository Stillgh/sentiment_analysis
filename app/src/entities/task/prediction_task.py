import uuid

from app.src.entities.task.prediction_request import PredictionRequest
from app.src.entities.task.prediction_result import PredictionResult


class PredictionTask:
    def __init__(self, id: uuid, prediction_request: PredictionRequest, prediction_result: PredictionResult):
        self.__id = id
        self.__prediction_request = prediction_request
        self.__prediction_result = prediction_result

    @property
    def id(self) -> uuid:
        return self.__id

    @id.setter
    def id(self, value: uuid):
        self.__id = value

    @property
    def prediction_request(self) -> PredictionRequest:
        return self.__prediction_request

    @prediction_request.setter
    def prediction_request(self, value: PredictionRequest):
        self.__prediction_request = value

    @property
    def prediction_result(self) -> PredictionResult:
        return self.__prediction_result

    @prediction_result.setter
    def prediction_result(self, value: PredictionResult):
        self.__prediction_result = value

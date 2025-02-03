import datetime
import uuid

from src.entities.model.inference_input import InferenceInput


class PredictionRequest:
    def __init__(self, user_id: uuid, model_id: uuid, inference_input: InferenceInput, request_timestamp: datetime, user_balance_before_task: float):
        self.__user_id = user_id
        self.__model_id = model_id
        self.__inference_input = inference_input
        self.__user_balance_before_task = user_balance_before_task
        self.__request_timestamp = request_timestamp

    @property
    def user_id(self) -> uuid:
        return self.__user_id

    @user_id.setter 
    def user_id(self, value: uuid):
        self.__user_id = value

    @property
    def model_id(self) -> uuid:
        return self.__model_id

    @model_id.setter
    def model_id(self, value: uuid):
        self.__model_id = value

    @property
    def inference_input(self) -> InferenceInput:
        return self.__inference_input

    @inference_input.setter
    def inference_input(self, value: InferenceInput):
        self.__inference_input = value

    @property
    def user_balance_before_task(self) -> float:
        return self.__user_balance_before_task

    @user_balance_before_task.setter
    def user_balance_before_task(self, value: float):
        self.__user_balance_before_task = value

    @property
    def request_timestamp(self) -> datetime:
        return self.__request_timestamp

    @request_timestamp.setter
    def request_timestamp(self, value: datetime):
        self.__request_timestamp = value

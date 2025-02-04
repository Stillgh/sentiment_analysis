import abc
import uuid
from abc import ABC

from app.src.entities.ml_model.inference_input import InferenceInput


class MLModel(ABC):
    def __init__(self, model_id: uuid, name: str, model_type: str, prediction_cost: float):
        self.__model_id = model_id
        self.__name = name
        self.__model_type = model_type
        self.__prediction_cost = prediction_cost

    @property
    def id(self) -> uuid:
        return self.__model_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def model_type(self) -> str:
        return self.__model_type

    @property
    def prediction_cost(self) -> float:
        return self.__prediction_cost

    @name.setter
    def name(self, value: str):
        self.__name = value

    @model_type.setter
    def model_type(self, value: str):
        self.__model_type = value

    @prediction_cost.setter
    def prediction_cost(self, value: float):
        self.__prediction_cost = value

    @abc.abstractmethod
    def predict(self, data_input: InferenceInput):
        pass
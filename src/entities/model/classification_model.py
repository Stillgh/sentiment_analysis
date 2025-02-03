import uuid

from sklearn.base import BaseEstimator
import numpy as np

from src.entities.model.inference_input import InferenceInput
from src.entities.model.ml_model import MLModel


class ClassificationModel(MLModel):
    def __init__(self, model_id: uuid, name: str, model: BaseEstimator, prediction_cost: float):
        super().__init__(model_id, name, "classification", prediction_cost)
        self.__model = model

    @property
    def model(self) -> BaseEstimator:
        return self.__model

    @model.setter
    def model(self, model: BaseEstimator):
        self.__model = model

    def predict(self, data_input: InferenceInput):
        X = np.array(data_input)
        return self.__model.predict(X)


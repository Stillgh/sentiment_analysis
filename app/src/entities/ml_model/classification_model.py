from pydantic import PrivateAttr
from sklearn.base import BaseEstimator
import numpy as np

from entities.ml_model.inference_input import InferenceInput
from entities.ml_model.ml_model import MLModel
from sqlmodel import Field


class ClassificationModel(MLModel, table=True):
    __tablename__ = "ml_models"

    model_type: str = Field(default="classification", const=True)
    _model: BaseEstimator = PrivateAttr()

    def predict(self, data_input: InferenceInput):
        X = np.array(data_input.data)
        return self._model.predict(X)

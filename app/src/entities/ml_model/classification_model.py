from typing import Optional

import torch
from pydantic import PrivateAttr

from entities.ml_model.inference_input import InferenceInput
from entities.ml_model.ml_model import MLModel
from sqlmodel import Field


class ClassificationModel(MLModel, table=True):
    __tablename__ = "ml_models"

    model_type: str = Field(default="classification", const=True)
    _model: Optional[torch.nn.Module] = PrivateAttr(default=None)
    _tokenizer: Optional[object] = PrivateAttr(default=None)

    def set_resources(self, model: torch.nn.Module, tokenizer: object):
        self._model = model
        self._tokenizer = tokenizer
        print("Resources have been set manually.")

    def predict(self, data_input: InferenceInput):
        texts = data_input.data
        if self._model is None or self._tokenizer is None:
            raise ValueError("Model and tokenizer have not been loaded. "
                             "Call load_huggingface_resources() first.")

        inputs = self._tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self._model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        sentiment_map = {
            0: "Very Negative",
            1: "Negative",
            2: "Neutral",
            3: "Positive",
            4: "Very Positive"
        }
        predictions = torch.argmax(probabilities, dim=-1).tolist()
        return [sentiment_map[p] for p in predictions]





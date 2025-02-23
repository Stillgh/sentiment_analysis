import os

from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config.constants import DEFAULT_MODEL_NAME


class ModelLoader:
    def __init__(self, cache_dir: str = None):

        if cache_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml_models"))
            cache_dir = base_dir
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.loaded_models = {}

    # def load_default_from_hugging_face(self, repo: str = "tabularisai/multilingual-sentiment-analysis"):
    #     default_model = 'multisent'
    #     if default_model in self.loaded_models:
    #         return self.loaded_models[default_model]
    #
    #     local_path = os.path.join(self.cache_dir, default_model)
    #     if not os.path.exists(local_path):
    #         tokenizer = AutoTokenizer.from_pretrained(repo)
    #         model = AutoModelForSequenceClassification.from_pretrained(repo)
    #         model.save_pretrained(local_path)
    #         tokenizer.save_pretrained(local_path)
    #         print(f"Downloaded and saved model '{default_model}' to local cache at '{local_path}'.")
    #     else:
    #         print("model already loaded locally")
    #
    #     self.loaded_models[default_model] = (model, tokenizer)

    def get_model(self, model_name: str = DEFAULT_MODEL_NAME):
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]

        local_path = os.path.join(self.cache_dir, model_name)
        if os.path.exists(local_path):
            tokenizer = AutoTokenizer.from_pretrained(local_path)
            model = AutoModelForSequenceClassification.from_pretrained(local_path)
            print(f"Loaded model '{model_name}' from local cache at '{local_path}'. {model} {tokenizer}")
            self.loaded_models[model_name] = (model, tokenizer)
        else:
            repo: str = "tabularisai/multilingual-sentiment-analysis"
            tokenizer = AutoTokenizer.from_pretrained(repo)
            model = AutoModelForSequenceClassification.from_pretrained(repo)
            model_path = os.path.join(self.cache_dir, DEFAULT_MODEL_NAME)
            model.save_pretrained(model_path)
            tokenizer.save_pretrained(model_path)
            self.loaded_models[DEFAULT_MODEL_NAME] = (model, tokenizer)
            print(f"Downloaded and saved model '{DEFAULT_MODEL_NAME}' to local cache at '{model_path}'.")

        return self.loaded_models[model_name]

    
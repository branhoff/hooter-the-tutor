from models.openAI import OpenAIChatGPTModel
from models.octoAI import OctoAI

def choose_model(client: str):
    models = {
        "openAI": OpenAIChatGPTModel,
        "octoAI": OctoAI
    }

    model_class = models.get(client)
    if model_class:
        return model_class()
    else:
        raise ValueError(f"Model for client '{client}' is not defined.")
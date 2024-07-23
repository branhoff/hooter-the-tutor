import logging
import openai
import os

from dotenv import load_dotenv
from responses import get_hooter_explanation


logger = logging.getLogger(__name__)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenAIChatGPTModel:

    def __init__(self, model_name: str = "gpt-4o-mini", max_tokens: int = 1024, presence_penalty: float = 0.0, temperature: float = 0.7, top_p: float = 0.9):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.presence_penalty = presence_penalty
        self.temperature = temperature
        self.top_p = top_p
        openai.api_key = OPENAI_API_KEY

    def generate_response(self, user_message: str) -> str:
        lowered = user_message.lower()
        if "how does this accountability work again" in lowered or "explain the accountability system" in lowered:
            return get_hooter_explanation()
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant named Hooter the Tutor (<@1237247053180960830>) that specializes in helping people accomplish their study goals."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                presence_penalty=self.presence_penalty,
                temperature=self.temperature,
                top_p=self.top_p
            )
            logger.debug(response)
            return response.choices[0].message['content']
        except Exception as e:
            print(f"Error generating response from OpenAIChatGPTModel: {e}")
            return "Sorry, I couldn't generate a response."

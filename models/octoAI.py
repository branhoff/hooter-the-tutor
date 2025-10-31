from dotenv import load_dotenv
import os
from langchain_community.llms.octoai_endpoint import OctoAIEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from responses import get_hooter_explanation


load_dotenv()
class OctoAI:
  def generate_response(self, user_message: str) -> str:
    lowered = user_message.lower()

    if "how does this accountability work again" in lowered or "explain the accountability system" in lowered:
      return get_hooter_explanation()
    else:
      return ask_LLM(lowered)
    
def ask_LLM(lowered):
    # API token
    OCTOAI_API_TOKEN = os.environ.get("OCTOAI_API_TOKEN")
    if not OCTOAI_API_TOKEN:
        raise ValueError("OCTOAI_API_TOKEN is not set in the environment variables.")

    # Initialize llm
    llm = OctoAIEndpoint(
        model="mixtral-8x22b-instruct",
        max_tokens=5000,  
        presence_penalty=0,
        temperature=0.5,
        top_p=1
    )

    # prompt
    template = """You are a helpful, quirky tutor for helping people learn by doing question-answering tasks. Answer the question concisely and accurately, within 3 sentences. If you don't know the answer, just say that you don't know. If the question is inappropriate or contains profanity, refuse to answer.
    Question: {question} 
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)

    # Create a processing chain
    try:
        # Prepare the input for the prompt
        prompt_input = prompt.format(question=lowered)
        
        # Call the LLM with the prepared prompt
        llm_output = llm.invoke(prompt_input)
        
        # Parse the output using StrOutputParser
        output_parser = StrOutputParser()
        response = output_parser.parse(llm_output)
        
        return response

    except Exception as e:
        return f"An error occurred: {e}"

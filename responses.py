from dotenv import load_dotenv
import os
from langchain_community.embeddings import OctoAIEmbeddings
from langchain_community.llms.octoai_endpoint import OctoAIEndpoint
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

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



def get_hooter_explanation():
  """Returns the detailed explanation of the system."""
  return (
    "Here’s how our accountability system keeps you on track:\n"
    "• **Join the Accountability Room:** When you join, please share your goal for the session. Stay for at least 25 minutes to count towards your accountability streak.\n"
    "• **Daily Accountability Sessions:** Every day at 9 PM PST, we hold a group accountability session. You're encouraged to join us to work on your tasks with group support.\n"
    "• **Session Flexibility:** The streak system works asynchronously. As long as you join the Accountability Room for 25 minutes, it will count towards your streak, regardless of the time.\n"
    "• **Session Wrap-Up:** Before you leave, let us know what you accomplished and what's next on your agenda.\n"
    "• **Community Engagement:** Feel free to notify the group when you plan to work. Others might join you if the schedule fits!\n"
    "• **Track Your Progress:** I track both your current streak and your longest streak.\n\n"
    "Thinking about adding a 'streak freeze' feature:\n"
    "• **Streak Freeze:** Earn a freeze by consistently engaging for a set number of days. This can save your streak if you miss a day!\n"
    "What do you think? How many days should be required to earn a streak freeze?"
  )

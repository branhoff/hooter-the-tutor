import argparse
from dotenv import load_dotenv
import os
from langchain_community.embeddings import OctoAIEmbeddings
from langchain_community.llms.octoai_endpoint import OctoAIEndpoint
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def ask_LLM(lowered):
    # API token
    OCTOAI_API_TOKEN = os.environ.get("OCTOAI_API_TOKEN")
    if not OCTOAI_API_TOKEN:
        raise ValueError("OCTOAI_API_TOKEN is not set in the environment variables.")

    # Initialize llm
    llm = OctoAIEndpoint(
        model="meta-llama-3-8b-instruct",
        max_tokens=512,  
        presence_penalty=0,
        temperature=0.5,
        top_p=1,
        stop=["\n","Question:"],
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

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Ask a question using the LLM.")
    parser.add_argument("question", type=str, help="The question you want to ask the LLM.")

    # Parse the arguments
    args = parser.parse_args()

    # Get the response from the LLM
    response = ask_LLM(args.question.lower())

    # Print the response
    print(response)

if __name__ == "__main__":
    main()

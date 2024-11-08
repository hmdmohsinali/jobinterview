# app/services/langchain.py
import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI  # Ensure correct package
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Set Google API Key from environment variables
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')

# Initialize the Gemini model
chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

# Prompt Templates
question_prompt = PromptTemplate(
    input_variables=["category_name"],
    template="Generate a challenging interview question about {category_name}. Question should be within 1 to 3 lines"
)

feedback_prompt = PromptTemplate(
    input_variables=["question", "user_response"],
    template=(
        "As an expert interviewer, provide constructive feedback on the following answer.\n"
        "Question: {question}\nAnswer: {user_response}"
    )
)

# Asynchronous Functions

async def generate_question(category_name: str) -> str:
    """
    Generates an interview question based on the category.
    """
    prompt = question_prompt.format(category_name=category_name)
    try:
        # Run the model in a non-blocking way
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: chat.predict(prompt)
        )
        return response.strip()  # Clean up any extra spaces
    except Exception as e:
        print(f"Error generating question: {e}")
        return "Unable to generate a question at this time."

async def generate_feedback(question: str, user_response: str) -> str:
    """
    Generates feedback for a given question and user response.
    """
    prompt = feedback_prompt.format(question=question, user_response=user_response)
    try:
        # Run the model in a non-blocking way
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: chat.predict(prompt)
        )
        return response.strip()  # Clean up any extra spaces
    except Exception as e:
        print(f"Error generating feedback: {e}")
        return "Unable to generate feedback at this time."

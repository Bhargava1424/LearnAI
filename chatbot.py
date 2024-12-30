import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from google.cloud import texttospeech
from google.cloud import aiplatform
import google.generativeai as genai
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Load environment variables
load_dotenv()


# Set up Google Cloud credentials and project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT")

aiplatform.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"))

memory = ConversationBufferMemory()

# Define prompt template
template = """The following is a conversation with an AI assistant. The assistant is helpful, creative, and friendly.

{history}
Human: {input}
AI Assistant:"""
prompt = PromptTemplate(input_variables=["history", "input"], template=template)

# Generate response using Gemini AI
def generate_response(user_input, history):
    # Prepare history for the prompt
    formatted_history = "\n".join(history)
    input_text = f"{formatted_history}\nHuman: {user_input}\nAI Assistant:"

    # Generate text response
    model = genai.GenerativeModel("gemini-1.5-flash")  # Replace with specific Gemini model if needed
    response = model.generate_content([input_text])
    

    # Return AI response text
    return response.text

# Main chatbot loop
print("AI Chatbot Ready! Type 'exit' to end.")
chat_history = []
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    # Generate AI response
    ai_response = generate_response(user_input, chat_history)
    chat_history.append(f"Human: {user_input}")
    chat_history.append(f"AI Assistant: {ai_response}")

    print("AI Assistant:", ai_response)


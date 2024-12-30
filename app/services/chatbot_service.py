from typing import List
import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import google.generativeai as genai

class ChatbotService:
    def __init__(self):
        load_dotenv()
        
        # Set up Google Cloud credentials and project
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT")
        
        self.memory = ConversationBufferMemory()
        self.template = """The following is a conversation with an AI assistant. The assistant is helpful, creative, and friendly.

        {history}
        Human: {input}
        AI Assistant:"""
        self.prompt = PromptTemplate(input_variables=["history", "input"], template=self.template)

    def generate_response(self, user_input: str, chat_history: List[str]) -> str:
        # Prepare history for the prompt
        formatted_history = "\n".join(chat_history)
        input_text = f"{formatted_history}\nHuman: {user_input}\nAI Assistant:"

        # Generate text response
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([input_text])
        
        return response.text
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai

class ChatbotService:
    def __init__(self):
        load_dotenv()
        
        # Set up Google Cloud credentials and project
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT")
        
        # Connect to MongoDB with correct database name
        try:
            client = MongoClient(os.getenv("MONGO_URI"))
            self.db = client['chitAI']  # Changed from 'chitfundDB' to 'chitAI'
            self.users_collection = self.db['users']
            
            # Debug: Print collection info
            print("Connected to database:", self.db.name)
            print("Collections:", self.db.list_collection_names())
            
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            raise e

        # Memory and Prompt
        self.memory = ConversationBufferMemory()
        self.template = """The following is a conversation with an AI assistant. The assistant is helpful, creative, and friendly.

        Context: The assistant has access to user profiles, chit funds, and hosts. Use this information to assist users.

        {history}
        Human: {input}
        AI Assistant:"""
        self.prompt = PromptTemplate(input_variables=["history", "input"], template=self.template)

    def get_user_data(self, user_id: str) -> Dict[Any, Any]:
        """Fetch user data and related chitfund and host information"""
        try:
            # Fetch user data
            user_data = self.users_collection.find_one({"userId": user_id})
            if not user_data:
                return {"error": f"User not found with ID: {user_id}"}

            # Fetch all chitfunds this user participates in
            chitfund_ids = user_data.get('chitFundsParticipated', [])
            chitfunds = list(self.db['chitfunds'].find({"_id": {"$in": chitfund_ids}}))

            # Fetch all hosts associated with these chitfunds
            host_ids = [cf['hostId'] for cf in chitfunds]
            hosts = list(self.db['hosts'].find({"_id": {"$in": host_ids}}))

            return {
                "user": {
                    "fullName": user_data.get('fullName'),
                    "email": user_data.get('email'),
                    "phone": user_data.get('phone'),
                    "preferredLanguage": user_data.get('preferredLanguage')
                },
                "payments": user_data.get('paymentHistory', []),
                "chitfunds_participated": chitfunds,
                "distributions_received": user_data.get('distributionsReceived', []),
                "hosts": hosts
            }
        except Exception as e:
            print(f"Error fetching data: {e}")
            return {"error": str(e)}

    def generate_response(self, user_input: str, chat_history: List[str], user_id: str) -> str:
        try:
            user_data = self.get_user_data(user_id)
            
            if "error" in user_data:
                return f"Error: {user_data['error']}"

            context = f"""
            You are a financial assistant for a chitfund company. You have access to complete user information:

            1. User Profile:
            - Name: {user_data['user']['fullName']}
            - Preferred Language: {user_data['user']['preferredLanguage']}

            2. Payment Records:
            ```
            {user_data['payments']}
            ```

            3. Chitfunds Participated In:
            ```
            {user_data['chitfunds_participated']}
            ```

            4. Distributions Received:
            ```
            {user_data['distributions_received']}
            ```

            5. Associated Hosts:
            ```
            {user_data['hosts']}
            ```

            You can answer questions about:
            - Payment history and status
            - Chitfund details (type, duration, value, etc.)
            - Distribution records and commissions
            - Host information and performance
            - Overall financial status
            - Participation details
            - Future payments and distributions
            - Any other chitfund-related queries

            Please provide accurate and helpful responses based on this data.
            """

            input_text = f"""
            Context: {context}
            
            Human: {user_input}
            Assistant: Please analyze all available information and provide a comprehensive response."""

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([input_text])
            
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
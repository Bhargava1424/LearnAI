from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.chatbot_service import ChatbotService

app = FastAPI(title="Chatbot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    app.state.chatbot = ChatbotService()

# New endpoint to test user data fetching
@app.get("/user/{user_id}")
async def get_user_data(user_id: str):
    chatbot = app.state.chatbot
    try:
        user_data = chatbot.get_user_data(user_id)
        if "error" in user_data:
            raise HTTPException(status_code=404, detail=user_data["error"])
        return user_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/chat")
async def chat(user_input: str, user_id: str = Query(...)):
    chatbot = app.state.chatbot
    chat_history = []
    try:
        response = chatbot.generate_response(user_input, chat_history, user_id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

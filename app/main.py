from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat_router
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

# Dependency to create ChatbotService instance
@app.on_event("startup")
async def startup_event():
    app.state.chatbot = ChatbotService()

# Include routers
app.include_router(chat_router.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
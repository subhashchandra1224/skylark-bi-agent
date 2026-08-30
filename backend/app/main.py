from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, chat
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Skylark BI Agent API")

# Configure CORS for frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
allow_origins = [frontend_url] if frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow your frontend origin (adjust if needed)
origins = [
    "http://localhost:5173",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SurveyInput(BaseModel):
    user_input: str

@app.post("/recommend")
async def recommend_video(data: SurveyInput):
    return {
        "videoUrl": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "message": "This is a static default video."
    }

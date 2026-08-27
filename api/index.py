import os
import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Resolve project root relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

app = FastAPI(title="MidtermVibe AI Learning Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_questions():
    q_file = DATA_DIR / "questions.json"
    if not q_file.exists():
        # Fallback to local copy in api or current dir
        q_file = Path("data/questions.json")
    if q_file.exists():
        with open(q_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.get("/api/questions")
def get_questions(
    track: Optional[str] = None,
    day: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None
):
    questions = load_questions()
    filtered = questions

    if track and track != "all":
        filtered = [q for q in filtered if track.lower() in q.get("track", "").lower()]
    
    if day and day != "all":
        filtered = [q for q in filtered if day.lower() in q.get("day", "").lower()]
        
    if difficulty and difficulty != "all":
        filtered = [q for q in filtered if q.get("difficulty", "").lower() == difficulty.lower()]
        
    if search:
        s = search.lower()
        filtered = [
            q for q in filtered
            if s in q.get("question", "").lower()
            or s in q.get("topic", "").lower()
            or s in q.get("explanation", "").lower()
        ]
        
    return {
        "total": len(filtered),
        "questions": filtered
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "platform": "Vercel Serverless"}

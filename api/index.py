import os
import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI20K Learning Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_questions():
    # Try multiple possible file locations on Vercel Serverless
    candidates = [
        Path(__file__).resolve().parent.parent / "data" / "questions.json",
        Path(__file__).resolve().parent / "data" / "questions.json",
        Path("data/questions.json"),
        Path("static/data/questions.json")
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue
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
        # Exact match first: "Day 23" must not also pull in "Day 23 / Track 3".
        exact = [q for q in filtered if q.get("day", "").lower() == day.lower()]
        if exact:
            filtered = exact
        else:
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
    return {"status": "ok", "platform": "Vercel"}

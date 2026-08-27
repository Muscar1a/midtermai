import os
import json
import random
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import markdown

app = FastAPI(title="MidtermVibe AI Learning Platform")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = BASE_DIR / "content"
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

def load_questions():
    q_file = DATA_DIR / "questions.json"
    if q_file.exists():
        with open(q_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_flashcards():
    fc_file = DATA_DIR / "flashcards.json"
    if fc_file.exists():
        with open(fc_file, "r", encoding="utf-8") as f:
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
            or any(s in opt.lower() for opt in q.get("options", []))
            or s in q.get("explanation", "").lower()
        ]
        
    return {
        "total": len(filtered),
        "questions": filtered
    }

@app.get("/api/random-quiz")
def get_random_quiz(
    count: int = Query(10, ge=1, le=100),
    track: Optional[str] = None,
    difficulty: Optional[str] = None
):
    questions = load_questions()
    filtered = questions
    
    if track and track != "all":
        filtered = [q for q in filtered if track.lower() in q.get("track", "").lower()]
    if difficulty and difficulty != "all":
        filtered = [q for q in filtered if q.get("difficulty", "").lower() == difficulty.lower()]
        
    if not filtered:
        return {"questions": [], "count": 0}
        
    sampled_count = min(count, len(filtered))
    quiz_questions = random.sample(filtered, sampled_count)
    
    return {
        "count": len(quiz_questions),
        "questions": quiz_questions
    }


@app.get("/api/content/tree")
def get_content_tree():
    if not CONTENT_DIR.exists():
        return {"tree": []}
        
    tree = []
    for section_dir in sorted(CONTENT_DIR.iterdir()):
        if section_dir.is_dir():
            sec_item = {"name": section_dir.name, "files": []}
            for md_file in sorted(section_dir.rglob("*.md")):
                rel_path = str(md_file.relative_to(CONTENT_DIR)).replace("\\", "/")
                sec_item["files"].append({
                    "name": md_file.stem,
                    "rel_path": rel_path,
                    "folder": md_file.parent.name
                })
            tree.append(sec_item)
    return {"tree": tree}

@app.get("/api/content/file")
def get_content_file(path: str):
    target_path = (CONTENT_DIR / path).resolve()
    if not str(target_path).startswith(str(CONTENT_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
        
    with open(target_path, "r", encoding="utf-8") as f:
        md_text = f.read()
        
    html_content = markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables", "nl2br"]
    )
    
    return {
        "path": path,
        "title": target_path.stem,
        "raw_markdown": md_text,
        "html_content": html_content
    }

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>MidtermVibe Study App is running! Please check static/index.html</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)

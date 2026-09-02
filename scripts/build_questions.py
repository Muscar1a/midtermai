#!/usr/bin/env python3
"""Build data/questions.json from per-day authored question files.

Each per-day file in scripts/qbank/ holds 30 questions with the minimal fields
(topic, difficulty, question, options, correct_index, explanation, slide_ref).
This script attaches id/track/day/correct_answer and validates the result.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QBANK = os.path.join(HERE, "qbank")
OUT = os.path.join(ROOT, "data", "questions.json")

P1 = "Phase 1: COMP2010"
T2 = "Track 2: Infrastructure"

# (file stem, day label, track, lesson title as it appears on the slide deck)
DAYS = [
    ("day01", "Day 01", P1, "Nhập Môn AI, LLM & Agent"),
    ("day02", "Day 02", P1, "Xác Định Bài Toán AI: Rule, Workflow hay Agent?"),
    ("day03", "Day 03", P1, "Từ Chatbot Đến Agentic Agent"),
    ("day04", "Day 04", P1, "Prompt Engineering & Tool Calling"),
    ("day05", "Day 05", P1, "AI Product Thinking & Requirements"),
    ("day06", "Day 06", P1, "AI Product & Project Management"),
    ("day07", "Day 07", P1, "Data Foundations: Embedding & Vector Store"),
    ("day08", "Day 08", P1, "RAG Pipeline"),
    ("day09", "Day 09", P1, "Multi-Agent & Kết Nối Hệ Thống"),
    ("day10", "Day 10", P1, "Data Pipeline & Data Observability"),
    ("day11", "Day 11", P1, "Guardrails, HITL & Responsible AI"),
    ("day12", "Day 12", P1, "Deployment — Đưa Agent Lên Cloud"),
    ("day13", "Day 13", P1, "Monitoring, Logging & Observability"),
    ("day14", "Day 14", P1, "AI Evaluation & Benchmarking"),
    ("day15", "Day 15", P1, "Triển Khai Thực Tế, Chi Phí Vận Hành & Định Hướng"),
    ("day16", "Day 16", T2, "Cloud Infrastructure for AI"),
    ("day17", "Day 17", T2, "Data Pipeline Engineering"),
    ("day18", "Day 18", T2, "Data Lakehouse Architecture"),
    ("day19", "Day 19", T2, "Vector Store & Feature Store"),
    ("day20", "Day 20", T2, "Model Serving & Inference Optimization"),
    ("day21", "Day 21", T2, "CI/CD for AI Systems"),
    ("day22", "Day 22", T2, "LLMOps & Prompt Versioning"),
    ("day23", "Day 23", T2, "Disaster Recovery & High Availability"),
    ("day23_track3", "Day 23 / Track 3", P1, "LangGraph & Agentic Orchestration"),
    ("day24", "Day 24", T2, "Data Governance & Security"),
    ("day25", "Day 25", T2, "GPU FinOps & Cost Optimization"),
    ("day26", "Day 26", T2, "MCP & A2A Infrastructure"),
    ("day27", "Day 27", T2, "Data Observability & Lineage"),
    ("day28", "Day 28", T2, "Platform Engineering & Documentation"),
]

REQUIRED = {"topic", "difficulty", "question", "options", "correct_index",
            "explanation", "slide_ref"}
DIFFICULTIES = ("Easy", "Medium", "Hard")


def slug(stem):
    return stem.replace("day", "day_", 1) if stem.startswith("day") else stem


def check_day(day, items, errors):
    if len(items) != 30:
        errors.append(f"{day}: expected 30 questions, got {len(items)}")
    counts = Counter(q.get("difficulty") for q in items)
    for d in DIFFICULTIES:
        if counts.get(d) != 10:
            errors.append(f"{day}: {d} count is {counts.get(d, 0)}, expected 10")

    seen_q = set()
    for i, q in enumerate(items, 1):
        where = f"{day} #{i}"
        missing = REQUIRED - set(q)
        if missing:
            errors.append(f"{where}: missing fields {sorted(missing)}")
            continue
        if q["difficulty"] not in DIFFICULTIES:
            errors.append(f"{where}: bad difficulty {q['difficulty']!r}")
        opts = q["options"]
        if not isinstance(opts, list) or len(opts) != 4:
            errors.append(f"{where}: expected 4 options, got {len(opts)}")
            continue
        if len(set(opts)) != 4:
            errors.append(f"{where}: duplicate options")
        if not isinstance(q["correct_index"], int) or not 0 <= q["correct_index"] <= 3:
            errors.append(f"{where}: correct_index out of range")
        text = q["question"].strip()
        if text in seen_q:
            errors.append(f"{where}: duplicate question text")
        seen_q.add(text)
        for o in opts:
            if not str(o).strip():
                errors.append(f"{where}: empty option")


def main():
    all_questions = []
    errors = []
    missing_files = []

    for stem, day, track, day_title in DAYS:
        path = os.path.join(QBANK, f"{stem}.json")
        if not os.path.exists(path):
            missing_files.append(stem)
            continue
        with open(path, encoding="utf-8") as fh:
            items = json.load(fh)
        check_day(day, items, errors)
        for i, q in enumerate(items, 1):
            all_questions.append({
                "id": f"{slug(stem)}_{i:03d}",
                "track": track,
                "day": day,
                "day_title": day_title,
                "topic": q["topic"],
                "difficulty": q["difficulty"],
                "question": q["question"],
                "options": q["options"],
                "correct_index": q["correct_index"],
                "correct_answer": q["options"][q["correct_index"]],
                "explanation": q["explanation"],
                "slide_ref": q["slide_ref"],
            })

    if missing_files:
        print("Missing day files: " + ", ".join(missing_files))
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print("  -", e)
        return 1

    by_day = Counter(q["day"] for q in all_questions)
    for _, day, _, _ in DAYS:
        if day in by_day:
            c = Counter(q["difficulty"] for q in all_questions if q["day"] == day)
            print(f"  OK {day}: E={c['Easy']} M={c['Medium']} H={c['Hard']} total={by_day[day]}")

    print(f"\nTotal questions: {len(all_questions)}")
    if missing_files:
        print("Not written — some days are still missing.")
        return 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(all_questions, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

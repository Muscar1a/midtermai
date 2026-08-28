"""
Automated Test Suite for Server Endpoints and Full 1,305-Question Dataset.
"""
import sys
import os
import json
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import app

def run_tests():
    print("=" * 60)
    print("🧪 RUNNING AUTOMATED SERVER & DATASET INTEGRATION TESTS")
    print("=" * 60)

    client = TestClient(app)

    # 1. Test full questions endpoint
    res = client.get("/api/questions")
    assert res.status_code == 200, f"Failed /api/questions: {res.status_code}"
    data = res.json()
    total = data.get("total")
    assert total == 1305, f"Expected total 1305, got {total}"
    print(f"✅ Total Questions Endpoint: 1,305 / 1,305")

    # 2. Test difficulty filters
    easy_res = client.get("/api/questions?difficulty=Easy").json()
    assert easy_res["total"] == 435, f"Expected 435 Easy, got {easy_res['total']}"
    print(f"✅ Difficulty Easy Filter: 435 / 435")

    med_res = client.get("/api/questions?difficulty=Medium").json()
    assert med_res["total"] == 522, f"Expected 522 Medium, got {med_res['total']}"
    print(f"✅ Difficulty Medium Filter: 522 / 522")

    hard_res = client.get("/api/questions?difficulty=Hard").json()
    assert hard_res["total"] == 348, f"Expected 348 Hard, got {hard_res['total']}"
    print(f"✅ Difficulty Hard Filter: 348 / 348")

    # 3. Test all 29 individual days
    all_days = [
        "Day 01", "Day 02", "Day 03", "Day 04", "Day 05",
        "Day 06", "Day 07", "Day 08", "Day 09", "Day 10",
        "Day 11", "Day 12", "Day 13", "Day 14", "Day 15",
        "Day 23 / Track 3",
        "Day 16", "Day 17", "Day 18", "Day 19", "Day 20",
        "Day 21", "Day 22", "Day 23", "Day 24", "Day 25",
        "Day 26", "Day 27", "Day 28"
    ]
    assert len(all_days) == 29

    for day_name in all_days:
        if day_name == "Day 23":
            # Pass track to distinguish Track 2 Day 23 from Phase 1 Day 23 / Track 3
            day_res = client.get(f"/api/questions?day={day_name}&track=Infrastructure").json()
        elif day_name == "Day 23 / Track 3":
            day_res = client.get(f"/api/questions?day={day_name}").json()
        else:
            day_res = client.get(f"/api/questions?day={day_name}").json()

        assert day_res["total"] == 45, f"Expected 45 for {day_name}, got {day_res['total']}"
        qs = day_res["questions"]
        easy_count = sum(1 for q in qs if q["difficulty"] == "Easy")
        med_count = sum(1 for q in qs if q["difficulty"] == "Medium")
        hard_count = sum(1 for q in qs if q["difficulty"] == "Hard")
        assert easy_count == 15, f"{day_name} Easy: {easy_count}"
        assert med_count == 18, f"{day_name} Med: {med_count}"
        assert hard_count == 12, f"{day_name} Hard: {hard_count}"

    print(f"✅ All 29 Days Verified (Exactly 45 questions each: 15 Easy, 18 Med, 12 Hard)")

    # 4. Test Random Quiz Endpoint
    rand_res = client.get("/api/random-quiz?count=30").json()
    assert rand_res["count"] == 30, f"Expected 30 random questions, got {rand_res['count']}"
    print(f"✅ Random Quiz 30-Question Generator Verified")

    # 5. Test Static Files Availability
    static_file_path = "static/data/questions.json"
    assert os.path.exists(static_file_path), "static/data/questions.json does not exist"
    with open(static_file_path, "r", encoding="utf-8") as f:
        static_qs = json.load(f)
    assert len(static_qs) == 1305, f"Expected 1305 in static file, got {len(static_qs)}"
    print(f"✅ Static Offline JSON file Verified (1,305 items, {os.path.getsize(static_file_path)/(1024*1024):.2f} MB)")

    print("\n🎉 ALL 5 TEST SUITES PASSED WITH 100% ACCURACY!")

if __name__ == "__main__":
    run_tests()

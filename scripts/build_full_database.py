"""
Master Compilation & Verification Script for all 1,305 Questions across 29 Course Days.
Compiles and validates:
- Phase 1 (COMP2010): Days 01-15 + Day 23 / Track 3 (16 days = 720 questions)
- Track 2 (BIOM3010 Infrastructure): Days 16-28 (13 days = 585 questions)
Total: 29 days * 45 questions = 1,305 questions.
Saves to data/questions.json and static/data/questions.json.
"""

import sys
import os
import json
from collections import Counter

# Set UTF-8 encoding for console output
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.data_p1_days01_05 import get_days_01_to_05
from scripts.data_p1_days06_10 import get_days_06_to_10
from scripts.data_p1_days11_15_t3 import get_days_11_to_15_and_t3
from scripts.data_t2_days16_20 import get_days_16_to_20
from scripts.data_t2_days21_24 import get_days_21_to_24
from scripts.data_t2_days25_28 import get_days_25_to_28

def build_and_verify_all():
    print("=" * 70)
    print("🚀 COMPILING FULL 1,305-QUESTION DATASET ACROSS 29 COURSE DAYS")
    print("=" * 70)

    # 1. Gather all questions
    all_questions = []
    
    p1_01_05 = get_days_01_to_05()
    print(f"📦 Loaded Days 01-05 (Phase 1): {len(p1_01_05)} questions")
    all_questions.extend(p1_01_05)

    p1_06_10 = get_days_06_to_10()
    print(f"📦 Loaded Days 06-10 (Phase 1): {len(p1_06_10)} questions")
    all_questions.extend(p1_06_10)

    p1_11_15_t3 = get_days_11_to_15_and_t3()
    print(f"📦 Loaded Days 11-15 + Track 3 (Phase 1): {len(p1_11_15_t3)} questions")
    all_questions.extend(p1_11_15_t3)

    t2_16_20 = get_days_16_to_20()
    print(f"📦 Loaded Days 16-20 (Track 2): {len(t2_16_20)} questions")
    all_questions.extend(t2_16_20)

    t2_21_24 = get_days_21_to_24()
    print(f"📦 Loaded Days 21-24 (Track 2): {len(t2_21_24)} questions")
    all_questions.extend(t2_21_24)

    t2_25_28 = get_days_25_to_28()
    print(f"📦 Loaded Days 25-28 (Track 2): {len(t2_25_28)} questions")
    all_questions.extend(t2_25_28)

    print(f"\n📊 Total Compiled Questions: {len(all_questions)}")
    assert len(all_questions) == 1305, f"Expected 1305 questions, got {len(all_questions)}"

    # 2. Comprehensive Validation
    print("\n🔍 RUNNING RIGOROUS SCHEMA & INTEGRITY CHECKS...")
    
    seen_ids = set()
    days_counter = Counter()
    diff_per_day = {}
    track_counter = Counter()

    for idx, q in enumerate(all_questions, 1):
        # ID check
        q_id = q.get("id")
        assert q_id, f"Question #{idx} is missing 'id'"
        assert q_id not in seen_ids, f"Duplicate question ID: {q_id}"
        seen_ids.add(q_id)

        # Track check
        track = q.get("track")
        assert track, f"Question {q_id} missing 'track'"
        track_counter[track] += 1

        # Day check
        day = q.get("day")
        assert day, f"Question {q_id} missing 'day'"
        days_counter[day] += 1

        # Difficulty check
        diff = q.get("difficulty")
        assert diff in ["Easy", "Medium", "Hard"], f"Question {q_id} invalid difficulty: {diff}"
        if day not in diff_per_day:
            diff_per_day[day] = Counter()
        diff_per_day[day][diff] += 1

        # Question text check
        question_text = q.get("question")
        assert question_text and len(question_text.strip()) > 5, f"Question {q_id} question text too short"

        # Options check
        options = q.get("options")
        assert isinstance(options, list) and len(options) == 4, f"Question {q_id} options must have 4 items, got {options}"
        for opt_idx, opt in enumerate(options):
            assert isinstance(opt, str) and len(opt.strip()) > 0, f"Question {q_id} option #{opt_idx} is empty"

        # Correct index check
        c_idx = q.get("correct_index")
        assert c_idx in [0, 1, 2, 3], f"Question {q_id} invalid correct_index: {c_idx}"
        
        # Correct answer match check
        c_ans = q.get("correct_answer")
        assert c_ans == options[c_idx], f"Question {q_id} correct_answer mismatch: '{c_ans}' vs '{options[c_idx]}'"

        # Explanation check
        exp = q.get("explanation")
        assert exp and len(exp.strip()) > 10, f"Question {q_id} explanation is missing or too short"

        # Slide ref check
        ref = q.get("slide_ref")
        assert ref and len(ref.strip()) > 3, f"Question {q_id} slide_ref is missing"

    print("✅ All individual questions passed strict validation!")

    # 3. Check exact counts per day
    print("\n📅 PER-DAY BREAKDOWN VERIFICATION:")
    print("-" * 75)
    print(f"{'Day Name':<35} | {'Easy':<6} | {'Med':<6} | {'Hard':<6} | {'Total':<6} | {'Status'}")
    print("-" * 75)

    expected_days_count = 29
    assert len(days_counter) == expected_days_count, f"Expected {expected_days_count} days, found {len(days_counter)}"

    for day, count in days_counter.items():
        d_counts = diff_per_day[day]
        e = d_counts.get("Easy", 0)
        m = d_counts.get("Medium", 0)
        h = d_counts.get("Hard", 0)
        assert e == 15, f"{day} Easy count is {e}, expected 15"
        assert m == 18, f"{day} Medium count is {m}, expected 18"
        assert h == 12, f"{day} Hard count is {h}, expected 12"
        assert count == 45, f"{day} Total count is {count}, expected 45"
        print(f"{day:<35} | {e:<6} | {m:<6} | {h:<6} | {count:<6} | ✅ OK (45/45)")

    print("-" * 75)
    print(f"Total Unique Days: {len(days_counter)} days")
    print(f"Total Questions: {sum(days_counter.values())} questions")
    print(f"By Track:")
    for trk, cnt in track_counter.items():
        print(f"  - {trk}: {cnt} questions")

    # 4. Save to files
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/data', exist_ok=True)

    dest_paths = ['data/questions.json', 'static/data/questions.json']
    for path in dest_paths:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(all_questions, f, ensure_ascii=False, indent=2)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"\n💾 Saved full database to '{path}' ({size_mb:.2f} MB)")

    print("\n🎉 MASTER QUESTION DATABASE BUILD COMPLETE & 100% VERIFIED!")

if __name__ == '__main__':
    build_and_verify_all()

#!/usr/bin/env python3
"""
Replace lazy-prefix distractors with genuine distractors drawn from the
same-day / same-topic question pool.

Lazy pattern: 3 wrong options are copies of the correct answer prefixed with
"Phương pháp phân bổ tĩnh:", "Phương pháp ngoại tuyến theo lô:", or
"Phương pháp xử lý tuần tự:" and lowercased.

Strategy: use correct answers from OTHER questions in the same day as
distractors. They're topically relevant, professionally written, and test
whether the student can distinguish concepts learned in the same session.
"""

import json
import os
import random
from collections import defaultdict

LAZY_PREFIXES = [
    "phương pháp phân bổ tĩnh:",
    "phương pháp ngoại tuyến theo lô:",
    "phương pháp xử lý tuần tự:",
]


def is_lazy(opt):
    lower = opt.lower().strip()
    return any(lower.startswith(p) for p in LAZY_PREFIXES)


def word_set(text):
    return set(text.lower().split())


def jaccard(a, b):
    sa, sb = word_set(a), word_set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def is_formula(text):
    return any(c in text for c in ["=", "+", "/", "$"])


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base, "data", "questions.json")

    with open(data_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions")

    # Build pools: day -> list of (answer, topic, id)
    day_pool = defaultdict(list)
    for q in questions:
        day_pool[q["day"]].append(
            {"answer": q["correct_answer"], "topic": q.get("topic", ""), "id": q["id"]}
        )

    # Also build a global pool for fallback
    all_answers = [q["correct_answer"] for q in questions]

    stats = {"fixed": 0, "skipped": 0, "replaced_options": 0}

    for q in questions:
        opts = q["options"]
        ci = q["correct_index"]
        correct = q["correct_answer"]

        lazy_idx = [i for i in range(4) if i != ci and is_lazy(opts[i])]
        if not lazy_idx:
            continue

        need = len(lazy_idx)
        day = q["day"]
        topic = q.get("topic", "")
        correct_len = len(correct)
        correct_is_formula = is_formula(correct)

        # Texts already in the question (correct + non-lazy wrongs)
        existing_texts = {correct}
        for i in range(4):
            if i != ci and i not in lazy_idx:
                existing_texts.add(opts[i])

        # Gather candidates: same topic first, then same day, then adjacent days
        candidates = []
        seen_answers = set(existing_texts)

        def add_from_pool(pool_entries):
            for entry in pool_entries:
                a = entry["answer"]
                if a not in seen_answers and entry["id"] != q["id"]:
                    candidates.append(a)
                    seen_answers.add(a)

        # Same topic, same day
        same_topic = [
            e for e in day_pool.get(day, []) if e["topic"] == topic
        ]
        add_from_pool(same_topic)

        # Same day, other topics
        other_topic = [
            e for e in day_pool.get(day, []) if e["topic"] != topic
        ]
        add_from_pool(other_topic)

        # Score and filter candidates
        scored = []
        for c in candidates:
            sim = jaccard(correct, c)
            if sim > 0.65:
                continue

            c_len = len(c)
            len_ratio = c_len / correct_len if correct_len > 0 else 1.0

            # Prefer similar length
            if 0.3 <= len_ratio <= 3.0:
                len_score = 1.0 - min(abs(1.0 - len_ratio) * 0.4, 0.8)
            else:
                len_score = 0.05

            # Bonus for matching format (formula vs text)
            if is_formula(c) == correct_is_formula:
                len_score += 0.15

            scored.append((len_score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        available = [c for _, c in scored]

        if len(available) < need:
            stats["skipped"] += 1
            continue

        # Pick distractors with diversity check
        rng = random.Random(f"strengthen_v1_{q['id']}")
        top_pool = available[: max(need * 4, 15)]
        rng.shuffle(top_pool)

        selected = []
        for candidate in top_pool:
            if len(selected) >= need:
                break
            # Check diversity: not too similar to any already selected
            if all(jaccard(candidate, s) < 0.55 for s in selected):
                # Also not too similar to kept non-lazy wrong options
                if all(jaccard(candidate, k) < 0.55 for k in existing_texts if k != correct):
                    selected.append(candidate)

        if len(selected) < need:
            # Relax diversity constraint
            for candidate in top_pool:
                if len(selected) >= need:
                    break
                if candidate not in selected:
                    selected.append(candidate)

        if len(selected) < need:
            stats["skipped"] += 1
            continue

        # Replace lazy options
        new_opts = list(opts)
        for i, li in enumerate(lazy_idx):
            new_opts[li] = selected[i]

        # Verify no duplicates
        if len(set(new_opts)) < 4:
            stats["skipped"] += 1
            continue

        # Shuffle deterministically
        rng2 = random.Random(f"shuffle_v1_{q['id']}")
        rng2.shuffle(new_opts)
        new_ci = new_opts.index(correct)

        q["options"] = new_opts
        q["correct_index"] = new_ci

        assert q["options"][q["correct_index"]] == q["correct_answer"]

        stats["fixed"] += 1
        stats["replaced_options"] += need

    # Verify no lazy prefixes remain in fixed questions
    remaining_lazy = 0
    for q in questions:
        for i, o in enumerate(q["options"]):
            if i != q["correct_index"] and is_lazy(o):
                remaining_lazy += 1

    print(f"\nResults:")
    print(f"  Fixed:    {stats['fixed']} questions")
    print(f"  Skipped:  {stats['skipped']} questions (not enough candidates)")
    print(f"  Replaced: {stats['replaced_options']} individual options")
    print(f"  Remaining lazy distractors: {remaining_lazy}")

    # Answer key distribution
    from collections import Counter

    idx_counts = Counter(q["correct_index"] for q in questions)
    print(f"\nAnswer key distribution:")
    for idx in range(4):
        letter = chr(65 + idx)
        count = idx_counts.get(idx, 0)
        pct = count / len(questions) * 100
        print(f"  {letter}: {count} ({pct:.1f}%)")

    # Save to all paths
    paths = [
        os.path.join(base, "data", "questions.json"),
        os.path.join(base, "static", "data", "questions.json"),
        os.path.join(base, "api", "data", "questions.json"),
    ]
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        size_kb = os.path.getsize(p) / 1024
        print(f"  Saved: {p} ({size_kb:.0f} KB)")

    # Sample output for verification
    print(f"\n=== Sample fixed questions ===")
    fixed_qs = [q for q in questions if not any(is_lazy(o) for i, o in enumerate(q["options"]) if i != q["correct_index"])]
    rng_sample = random.Random(42)
    samples = rng_sample.sample(fixed_qs, min(5, len(fixed_qs)))
    for q in samples:
        ci = q["correct_index"]
        print(f"\n--- {q['id']} ({q['difficulty']}) ---")
        print(f"Q: {q['question'][:100]}...")
        for i, o in enumerate(q["options"]):
            mark = "[CORRECT]" if i == ci else "         "
            print(f"  {mark} {o[:110]}")


if __name__ == "__main__":
    main()

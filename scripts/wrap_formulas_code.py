#!/usr/bin/env python3
"""
Wrap plain-text math formulas in backticks (`...`) so they render as <code>
in the frontend. Simpler and more readable than LaTeX for these formulas.
"""

import json
import os
import re


def extract_formula_end(text, start):
    """Find where a math formula ends, tracking parentheses."""
    i = start
    n = len(text)
    depth = 0

    while i < n:
        c = text[i]
        if c == '(':
            depth += 1
        elif c == ')':
            if depth > 0:
                depth -= 1
            else:
                break
        elif c in '.;' and depth == 0:
            if c == '.' and i + 1 < n and text[i + 1].isdigit():
                i += 1
                continue
            break
        elif c == ',' and depth == 0:
            if i + 1 < n and text[i + 1].isdigit():
                i += 1
                continue
            break
        elif c == '\n':
            break
        i += 1

    return i


def wrap_formulas_in_code(text):
    """Wrap plain-text math formulas in backticks."""
    if not text:
        return text

    # Protect existing backtick code and LaTeX
    protected = []

    def protect(m):
        protected.append(m.group())
        return f"\x00{len(protected) - 1}\x00"

    result = re.sub(r'`[^`]+`', protect, text)
    result = re.sub(r'\$\$[\s\S]*?\$\$', protect, result)
    result = re.sub(r'\$[^\$\n]+?\$', protect, result)

    # Match equation patterns: Cost = ..., Latency = ..., etc.
    pattern = re.compile(
        r'(?:Total\s+)?(?:Cost|Latency)\s*=\s*'
    )

    new_parts = []
    pos = 0
    for m in pattern.finditer(result):
        start = m.start()
        eq_end = m.end()
        end = extract_formula_end(result, eq_end)
        content = result[eq_end:end].rstrip()

        # Only wrap if it has math operators
        has_math = bool(re.search(r'[*/+\-]', content))
        if has_math and len(content) > 3:
            full = result[start:end].rstrip()
            new_parts.append(result[pos:start])
            new_parts.append(f'`{full}`')
            pos = end

    new_parts.append(result[pos:])
    result = ''.join(new_parts)

    # Restore protected blocks
    result = re.sub(r'\x00(\d+)\x00', lambda m: protected[int(m.group(1))], result)

    return result


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base, "data", "questions.json")

    with open(data_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions")

    changed = 0
    for q in questions:
        modified = False

        for field in ["question", "explanation"]:
            new_val = wrap_formulas_in_code(q[field])
            if new_val != q[field]:
                q[field] = new_val
                modified = True

        new_opts = [wrap_formulas_in_code(o) for o in q["options"]]
        if new_opts != q["options"]:
            q["options"] = new_opts
            q["correct_answer"] = q["options"][q["correct_index"]]
            modified = True

        if modified:
            changed += 1

    print(f"  Wrapped formulas: {changed} questions")

    # Verify answers
    mismatches = sum(1 for q in questions if q["options"][q["correct_index"]] != q["correct_answer"])
    print(f"  Answer mismatches: {mismatches}")

    # Show wrapped formulas
    print(f"\n=== Wrapped formulas ===")
    shown = set()
    for q in questions:
        for o in q["options"]:
            if '`Cost' in o or '`Total Latency' in o or '`Latency' in o:
                key = o[:80]
                if key not in shown:
                    shown.add(key)
                    print(f"  {o[:140]}")

    # Save
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


if __name__ == "__main__":
    main()

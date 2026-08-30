#!/usr/bin/env python3
"""
Fix LaTeX rendering in questions.json:
1. Escape $ used for currency/units so KaTeX ignores them
2. Wrap plain-text math formulas (Cost=..., Latency=...) in $...$
"""

import json
import os
import re


def fix_dollar_signs(text):
    """Escape non-LaTeX $ signs (currency, shell vars, units)."""
    if not text or '$' not in text:
        return text

    result = []
    n = len(text)
    i = 0

    while i < n:
        if text[i] != '$':
            result.append(text[i])
            i += 1
            continue

        # Already escaped: \$
        if i > 0 and text[i - 1] == '\\':
            result.append('$')
            i += 1
            continue

        # Display math: $$...$$
        if i + 1 < n and text[i + 1] == '$':
            close = text.find('$$', i + 2)
            if close != -1:
                result.append(text[i:close + 2])
                i = close + 2
                continue

        # Try to match as inline LaTeX: $content$
        j = i + 1
        while j < n and text[j] != '$' and text[j] != '\n':
            j += 1

        if j < n and text[j] == '$':
            content = text[i + 1:j]
            # Real LaTeX: has \commands, ^, _, {}, =, or is a single letter, or has spaced vars
            is_latex = bool(re.search(r'[\\^_{}=]|^[a-zA-Z]$|\\[a-z]|[a-z]\s+[a-z]', content, re.I))
            if is_latex:
                result.append(text[i:j + 1])
                i = j + 1
                continue

        # Not LaTeX — escape it
        result.append('\\$')
        i += 1

    return ''.join(result)


def extract_formula(text, start):
    """Extract a complete math formula starting at 'start' (after = sign).
    Tracks parentheses and returns the end position."""
    i = start
    n = len(text)
    depth = 0
    has_math = False

    while i < n:
        c = text[i]
        if c == '(':
            depth += 1
        elif c == ')':
            if depth > 0:
                depth -= 1
            else:
                break
        elif c in '*/+-':
            has_math = True
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

    return i, has_math


def wrap_math_equations(text):
    """Wrap plain-text equations in $...$."""
    if not text:
        return text

    # Protect existing LaTeX and code
    protected = []

    def protect(m):
        protected.append(m.group())
        return f"\x00{len(protected) - 1}\x00"

    result = re.sub(r'\$\$[\s\S]*?\$\$', protect, text)
    result = re.sub(r'\$[^\$\n]+?\$', protect, result)
    result = re.sub(r'`[^`]+`', protect, result)
    result = re.sub(r'\\\$', protect, result)

    # Find equation start patterns
    pattern = re.compile(
        r'(?:Total\s+)?(?:Cost|Latency)\s*=\s*'
    )

    new_parts = []
    pos = 0
    for m in pattern.finditer(result):
        start = m.start()
        eq_end = m.end()

        end, has_math = extract_formula(result, eq_end)
        content = result[eq_end:end].rstrip()

        if has_math and len(content) > 3:
            full = result[start:end].rstrip()
            # Replace * with \times for LaTeX
            latex = full.replace('*', r' \times ')
            latex = re.sub(r'\s+', ' ', latex).strip()
            new_parts.append(result[pos:start])
            new_parts.append(f'${latex}$')
            pos = end

    new_parts.append(result[pos:])
    result = ''.join(new_parts)

    # Power notation: 10^6
    result = re.sub(
        r'(?<!\$)(?<![\\])(\d+)\^(\d+|[a-z])(?![}\d])(?!\$)',
        lambda m: f'${m.group(1)}^{{{m.group(2)}}}$',
        result
    )

    # Restore
    result = re.sub(r'\x00(\d+)\x00', lambda m: protected[int(m.group(1))], result)

    return result


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base, "data", "questions.json")

    with open(data_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions")

    # Step 1: Fix dollar signs
    dollar_fixes = 0
    for q in questions:
        for field in ["question", "explanation"]:
            new_val = fix_dollar_signs(q[field])
            if new_val != q[field]:
                q[field] = new_val
                dollar_fixes += 1
        new_opts = [fix_dollar_signs(o) for o in q["options"]]
        if new_opts != q["options"]:
            q["options"] = new_opts
            q["correct_answer"] = q["options"][q["correct_index"]]
            dollar_fixes += 1

    print(f"  Dollar sign fixes: {dollar_fixes}")

    # Step 2: Wrap formulas
    formula_fixes = 0
    for q in questions:
        modified = False
        for field in ["question", "explanation"]:
            new_val = wrap_math_equations(q[field])
            if new_val != q[field]:
                q[field] = new_val
                modified = True
        new_opts = [wrap_math_equations(o) for o in q["options"]]
        if new_opts != q["options"]:
            q["options"] = new_opts
            q["correct_answer"] = q["options"][q["correct_index"]]
            modified = True
        if modified:
            formula_fixes += 1

    print(f"  Formula wraps: {formula_fixes}")

    # Verify
    broken = 0
    for q in questions:
        for text in [q["question"]] + q["options"] + [q["explanation"]]:
            t = text.replace('\\$', '')
            t = re.sub(r'\$\$[\s\S]*?\$\$', '', t)
            if t.count('$') % 2 != 0:
                broken += 1
                print(f"  BROKEN: {q['id']}: {text[:120]}")

    print(f"\n  Broken LaTeX: {broken}")

    if broken > 0:
        print("  WARNING: Not saving due to broken LaTeX!")
        return

    # Verify answers
    mismatches = sum(1 for q in questions if q["options"][q["correct_index"]] != q["correct_answer"])
    print(f"  Answer mismatches: {mismatches}")

    # Show wrapped Cost formulas
    print(f"\n=== Wrapped Cost/Latency formulas ===")
    shown = set()
    for q in questions:
        for o in q["options"]:
            if '$Cost' in o or '$Total Latency' in o or '$Latency' in o:
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

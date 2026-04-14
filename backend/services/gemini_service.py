from groq import Groq
import os
import re
import json
from dotenv import load_dotenv
from pyparsing import line
from pyparsing import line

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("✅ Groq configured")
DL_CONFIDENCE_THRESHOLD = float(os.getenv("DL_CONFIDENCE_THRESHOLD", "60"))


def detect_language_from_code(code: str) -> str:
    """Reliably detect language from raw code content, ignoring what the frontend reports."""
    c = code.lower()
    # Java — check before JS because both use 'class'
    if any([
        "class solution" in c and ("public " in c or "int " in c),
        "public int " in c,
        "public boolean " in c,
        "public string " in c,
        "public long " in c,
        "public void " in c,
        "public list<" in c,
        "public list" in c and "<" in c,
        "new int[" in c,
        "int[] " in c,
        "arraylist" in c,
        "hashmap" in c,
        "linked list" in c,
        "linkedlist" in c,
        "system.out" in c,
        "throws exception" in c,
    ]):
        return "java"
    # C++
    if any([
        "#include" in c,
        "vector<" in c,
        "unordered_map" in c,
        "cout <<" in c,
        "nullptr" in c,
        "std::" in c,
        "int main()" in c,
    ]):
        return "cpp"
    # Python
    if any([
        "def solution" in c,
        "def two_sum" in c,
        "self." in c,
        "def " in c and ":" in c,
        "import " in c and "from " in c,
        "print(" in c,
    ]):
        return "python"
    # JavaScript
    if any([
        "console.log" in c,
        "const " in c,
        "function " in c,
        "let " in c,
        "===" in c,
    ]):
        return "javascript"
    return "python"  # default fallback



def analyze_with_gemini(code: str, language: str, approach: str, confidence: float, all_scores: dict) -> dict:
    scores_text = "\n".join([
        f"  - {name}: {score}%"
        for name, score in all_scores.items()
    ])
    allowed_labels_text = ", ".join([str(k) for k in all_scores.keys()])

    prompt = f"""
You are an expert coding coach analyzing a student's code submission.

DL predicted approach:
- DL Approach: {approach} (confidence: {confidence}%)
DL confidence threshold: {DL_CONFIDENCE_THRESHOLD}%

Allowed approach labels (choose ONLY from these):
{allowed_labels_text}

Here is the student's code in {language}:
```
{code}
```


You must output a structured analysis with exactly these sections:

1. FINAL APPROACH
Rules:
- If DL confidence is below the threshold, FINAL APPROACH MUST be the correct approach inferred from the code.
- If DL confidence is at/above the threshold, FINAL APPROACH MUST equal the DL Approach label exactly.
- FINAL APPROACH must be exactly one label from the allowed list.

2. APPROACH EXPLANATION
Explain in 2-3 sentences the approach used.

3. TIME COMPLEXITY
State the time complexity with a brief explanation.

4. SPACE COMPLEXITY
State the space complexity with a brief explanation.

5. OPTIMIZATION TIPS
Give exactly 3 tips using format: 1) tip 2) tip 3) tip

6. GOOD PRACTICES
Give exactly 2 things using format: 1) thing 2) thing

7. DIFFICULTY LEVEL
Rate as Beginner / Intermediate / Advanced with one sentence explanation.

Keep your response concise and student-friendly.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert coding coach. Use EXACTLY these section headers with no numbers, no markdown, no ## symbols: FINAL APPROACH, APPROACH EXPLANATION, TIME COMPLEXITY, SPACE COMPLEXITY, OPTIMIZATION TIPS, GOOD PRACTICES, DIFFICULTY LEVEL. For optimization tips use 1) 2) 3) format. For good practices use 1) 2) format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )

    raw_text = response.choices[0].message.content
    result = parse_response(raw_text)
    result["raw_response"] = raw_text
    return result


def parse_response(text: str) -> dict:
    sections = {
        "final_approach": "",
        "approach_explanation": "",
        "time_complexity": "",
        "space_complexity": "",
        "optimization_tips": [],
        "good_practices": [],
        "difficulty_level": ""
    }

    SECTION_MAP = {
        "FINAL APPROACH": "final_approach",
        "APPROACH EXPLANATION": "approach_explanation",
        "TIME COMPLEXITY": "time_complexity",
        "SPACE COMPLEXITY": "space_complexity",
        "OPTIMIZATION TIPS": "optimization_tips",
        "GOOD PRACTICES": "good_practices",
        "DIFFICULTY LEVEL": "difficulty_level",
    }

    # Split text into lines
    lines = text.strip().split('\n')
    
    current_section = None
    section_lines = {}

    for line in lines:
        # Clean the line
        clean = line.strip().replace('#', '').replace('*', '').strip()
        
        # Check if this line IS a section header (entire line matches)
        matched_header = None
        for header in SECTION_MAP:
            if clean.upper() == header:
                matched_header = header
                break
        
        if matched_header:
            current_section = SECTION_MAP[matched_header]
            section_lines[current_section] = []
        elif current_section and clean:
            section_lines.setdefault(current_section, []).append(clean)

    # Now convert collected lines to final values
    for section, lines_list in section_lines.items():
        if section in ("approach_explanation", "time_complexity",
                       "space_complexity", "difficulty_level"):
            sections[section] = " ".join(lines_list).strip()

        elif section in ("optimization_tips", "good_practices"):
            items = []
            for line in lines_list:
                match = re.match(r'^[\d]+[\.|\)]\s*(.+)', line)
                if match:
                    items.append(match.group(1).strip())
                elif line.startswith('-') or line.startswith('•'):
                    items.append(line[1:].strip())
            sections[section] = items

    return sections

# ── ADD THIS FUNCTION at the bottom of gemini_service.py ──

async def get_verdict_tips(code: str, language: str, problem_name: str, verdict: str) -> dict:

    # Always auto-detect language from code to avoid mismatch
    detected_language = detect_language_from_code(code)

    verdict_prompts = {
        "wrong_answer":          "The solution produces incorrect output for some test cases.",
        "time_limit_exceeded":   "The solution is too slow and exceeds the time limit.",
        "memory_limit_exceeded": "The solution uses too much memory.",
        "runtime_error":         "The solution crashes during execution.",
        "compilation_error":     "The solution has syntax or compilation errors.",
    }

    verdict_context = verdict_prompts.get(verdict, "The solution failed.")

    prompt = f"""
You are a coding mentor helping a student fix their LeetCode solution.

Problem: {problem_name}
Language: {detected_language}
Verdict: {verdict_context}

Code:
{code}

Give exactly 3 specific, actionable tips to fix this issue.
Focus on what is likely wrong based on the verdict type and the code.

Return ONLY a JSON object in this exact format with no extra text:
{{
  "verdict_tips": [
    "tip 1 here",
    "tip 2 here",
    "tip 3 here"
  ]
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.4,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


async def predict_correctness(code: str, language: str, problem_name: str) -> dict:
    # Always auto-detect language from code — do NOT trust what the frontend sends
    detected_language = detect_language_from_code(code)

    prompt = f"""You are an expert coding coach reviewing a student's LeetCode solution BEFORE it is run.

Problem: {problem_name}
Language: {detected_language}

IMPORTANT RULES:
- The language above ({detected_language}) has been auto-detected from the code itself. It is correct.
- Do NOT flag or mention any language mismatch in your response.
- Evaluate the code purely as {detected_language} code.
- Focus only on logic, correctness, edge cases, and efficiency.

Code:
```{detected_language}
{code}
```

Analyze the code carefully and predict whether it is likely correct or not.
Check for:
- Logical errors or wrong algorithm
- Common edge cases (empty input, single element, negative numbers, overflow)
- Off-by-one errors
- Obvious TLE patterns (nested loops that could be O(n²) or worse when O(n) is expected)
- Language-specific syntax errors (e.g., missing semicolons, unmatched braces, wrong keyword)
- Runtime issues specific to {detected_language}

Return ONLY a JSON object in this exact format with no extra text:
{{
  "prediction": "likely_correct" | "likely_wrong" | "likely_tle" | "likely_error" | "likely_compilation_error",
  "confidence": "high" | "medium" | "low",
  "summary": "One sentence summary of your verdict (do NOT mention language mismatch)",
  "issues": ["issue 1", "issue 2"]
}}

If no issues found, set issues to an empty array [].
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)
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


def analyze_with_gemini(code: str, approach: str, confidence: float, all_scores: dict) -> dict:
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

Here is the student's code:
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
Language: {language}
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

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.4,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)
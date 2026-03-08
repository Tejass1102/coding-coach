from groq import Groq
import os
import re
from dotenv import load_dotenv
from pyparsing import line
from pyparsing import line

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("✅ Groq configured")


def analyze_with_gemini(code: str, approach: str, confidence: float, all_scores: dict) -> dict:
    scores_text = "\n".join([
        f"  - {name}: {score}%"
        for name, score in all_scores.items()
    ])

    prompt = f"""
You are an expert coding coach analyzing a student's code submission.

Our deep learning model has already analyzed this code and detected:
- Primary Approach: {approach} (confidence: {confidence}%)
- All approach scores:
{scores_text}

Here is the student's code:
```
{code}
```

Based on this, provide a structured analysis with exactly these sections:

1. APPROACH EXPLANATION
Explain in 2-3 sentences what approach the student used

2. TIME COMPLEXITY
State the time complexity with a brief explanation.

3. SPACE COMPLEXITY
State the space complexity with a brief explanation.

4. OPTIMIZATION TIPS
Give exactly 3 tips using format: 1) tip 2) tip 3) tip

5. GOOD PRACTICES
Give exactly 2 things using format: 1) thing 2) thing

6. DIFFICULTY LEVEL
Rate as Beginner / Intermediate / Advanced with one sentence explanation.

Keep your response concise and student-friendly.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert coding coach. Use EXACTLY these section headers with no numbers, no markdown, no ## symbols: APPROACH EXPLANATION, TIME COMPLEXITY, SPACE COMPLEXITY, OPTIMIZATION TIPS, GOOD PRACTICES, DIFFICULTY LEVEL. For optimization tips use 1) 2) 3) format. For good practices use 1) 2) format."
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
        "approach_explanation": "",
        "time_complexity": "",
        "space_complexity": "",
        "optimization_tips": [],
        "good_practices": [],
        "difficulty_level": ""
    }

    SECTION_MAP = {
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
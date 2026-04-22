import re
import json
import httpx

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

_PROBLEM_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    topicTags {
      name
      slug
    }
    similarQuestions
  }
}
"""

_DAILY_QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      title
      titleSlug
      difficulty
    }
  }
}
"""


def _problem_name_to_slug(name: str) -> str:
    """
    Convert a human-readable problem name to a LeetCode URL slug.
    """
    name = re.sub(r"^\d+\.\s*", "", name)
    name = re.sub(r"[^a-zA-Z0-9\s\-]", "", name)
    return name.strip().lower().replace(" ", "-")


def fetch_problem_metadata(problem_name: str) -> dict:
    """
    Fetch topic tags and similar questions for a LeetCode problem.
    """
    slug = _problem_name_to_slug(problem_name)
    if not slug:
        return {"tags": [], "similar_questions": []}

    try:
        with httpx.Client(timeout=6.0) as client:
            resp = client.post(
                LEETCODE_GRAPHQL,
                json={"query": _PROBLEM_QUERY, "variables": {"titleSlug": slug}},
                headers={
                    "Content-Type": "application/json",
                    "Referer": "https://leetcode.com",
                    "User-Agent": "Mozilla/5.0",
                },
            )
        data = resp.json()
        question = (data.get("data") or {}).get("question") or {}
        
        # Parse tags
        topic_tags = question.get("topicTags") or []
        tags = [t["name"] for t in topic_tags if t.get("name")]
        
        # Parse similar questions (LeetCode returns a stringified JSON array here)
        similar_str = question.get("similarQuestions")
        similar = []
        if similar_str:
            parsed = json.loads(similar_str)
            for q in parsed:
                similar.append({
                    "title": q.get("title", ""),
                    "slug": q.get("titleSlug", ""),
                    "difficulty": q.get("difficulty", "")
                })
                
        return {"tags": tags, "similar_questions": similar[:3]} # max 3 similar
    except Exception as exc:
        print(f"⚠️  LeetCode metadata fetch failed for '{problem_name}': {exc}")
        return {"tags": [], "similar_questions": []}


def fetch_daily_challenge() -> dict:
    """
    Fetch the active daily challenge from LeetCode.
    """
    try:
        with httpx.Client(timeout=6.0) as client:
            resp = client.post(
                LEETCODE_GRAPHQL,
                json={"query": _DAILY_QUERY, "variables": {}},
                headers={
                    "Content-Type": "application/json",
                    "Referer": "https://leetcode.com",
                    "User-Agent": "Mozilla/5.0",
                },
            )
        data = resp.json()
        active = (data.get("data") or {}).get("activeDailyCodingChallengeQuestion") or {}
        q = active.get("question") or {}
        
        if not q.get("title"):
            return None
            
        return {
            "title": q.get("title"),
            "slug": q.get("titleSlug"),
            "difficulty": q.get("difficulty"),
            "date": active.get("date"),
            "link": active.get("link")
        }
    except Exception as exc:
        print(f"⚠️  LeetCode daily challenge fetch failed: {exc}")
        return None


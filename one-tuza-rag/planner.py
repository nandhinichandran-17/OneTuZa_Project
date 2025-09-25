# planner.py
from typing import List, Dict
import re

def simple_plan(question: str) -> List[str]:
    """
    Decompose the user's complex question into smaller sub-questions.
    Very simple heuristic decomposition:
    - split by 'and' or 'while' or commas for multiple parts
    - also add 'background' retrieval
    """
    q = question.strip()
    plan = []
    # always include a background query
    plan.append(f"Background: explain key terms for: {q}")
    # try split by conjunctions to get sub-questions
    parts = re.split(r"\band\b|\bwhile\b|\b,|\b;|\bbut\b", q, flags=re.I)
    parts = [p.strip() for p in parts if p.strip()]
    for p in parts[:3]:  # limit to 3 parts
        plan.append(p)
    # also add a "mitigation/recommendation" goal if question contains 'propose' or 'mitigation'
    if re.search(r"propose|mitigation|recommend|strateg", q, re.I):
        plan.append("Provide mitigation strategies / recommendations")
    return plan
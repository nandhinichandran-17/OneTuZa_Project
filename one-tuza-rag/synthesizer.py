# synthesizer.py
import os
from typing import List, Dict
import openai
from rich import print
import re

# Setup key
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = "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"


def safe_snippet(text: str, max_len: int = 180) -> str:
    """
    Return a clean snippet up to max_len, ending at a sentence boundary if possible.
    """
    text = text.strip().replace("\n", " ")
    if len(text) <= max_len:
        return text

    # Try to cut at last sentence end within limit
    sentences = re.split(r'(?<=[\.\?!])\s+', text)
    out = ""
    for s in sentences:
        if len(out) + len(s) <= max_len:
            out += s + " "
        else:
            break

    if not out:  # fallback if no sentence fits
        out = text[:max_len].rsplit(" ", 1)[0]

    return out.strip() + "…"


def short_summarize_texts(texts: List[Dict], max_chars: int = 1500) -> str:
    """
    Summarizer: Prefer OpenAI LLM. If unavailable, fallback to structured bullets.
    """
    if OPENAI_KEY:
        prompt = (
            "You are an expert research summarizer. "
            "Synthesize the following sources into a concise structured report with:\n"
            "- A title\n"
            "- Key findings in bullet points\n"
            "- A short conclusion\n\n"
            "Use inline citations like [Local:filename_chunk] or [Web:source] from the labels.\n"
            "Keep report <= 600 words.\n\nSources:\n"
        )
        for i, s in enumerate(texts):
            label = s.get("label", "")
            snippet = s["text"][:2000]
            prompt += f"---\nSource {i+1} ({label}):\n{snippet}\n"

        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=900
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print("[synthesizer] OpenAI call failed, using fallback:", e)

    # -------------------
    # Fallback summarizer
    # -------------------
    summary = "# Research Report\n\n## Key Findings\n"
    for s in texts:
        label = s.get("label", "")
        snippet = safe_snippet(s["text"], max_len=180)
        summary += f"- {snippet} ({label})\n"

    summary += "\n## Conclusion\n"
    summary += (
        "The above findings are drawn from both local and web sources. "
        "They highlight the main aspects of the research query and "
        "suggest directions for deeper exploration."
    )

    if len(summary) > max_chars:
        summary = summary[:max_chars] + "…"

    return summary


def build_report(question: str, plan: List[str], local_hits: List[Dict], web_hits: List[Dict]) -> Dict:
    # Create labelled combined list for summarizer
    sources = []
    for l in local_hits:
        sources.append({"label": f"Local:{l['source']}", "text": l["text"], "meta": l})
    for w in web_hits:
        sources.append({"label": f"Web:{w.get('source') or w.get('title')}", "text": w["text"], "meta": w})

    summary_md = short_summarize_texts(sources)

    # Traceability list
    citations = [
        {"label": s["label"], "source_text_snippet": safe_snippet(s["text"], max_len=300)}
        for s in sources
    ]

    return {
        "question": question,
        "plan": plan,
        "summary_markdown": summary_md,
        "citations": citations,
        "local_hits": local_hits,
        "web_hits": web_hits
    }

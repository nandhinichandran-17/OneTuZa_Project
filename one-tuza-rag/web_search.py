# web_search.py
import wikipedia
import requests
import os
from typing import List, Dict

def serpapi_search(query: str, max_results: int = 3) -> List[Dict]:
    """
    Query SerpAPI (if key present). Try to return up to max_results items.
    If fewer informative items are found, placeholders will be appended so
    the returned list length equals max_results.
    """
    key = os.getenv("SERPAPI_API_KEY")
    if not key:
        return []
    params = {
        "q": query,
        "api_key": key,
        "engine": "google",
        # request more candidates than needed to improve chance of filling max_results
        "num": max_results * 3
    }
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[serpapi_search] request failed: {e}")
        return [{"source": "serpapi:placeholder", "title": "No result", "text": "SerpAPI request failed."}
                for _ in range(max_results)]

    js = r.json()
    organic = js.get("organic_results", [])
    results: List[Dict] = []
    for o in organic:
        if len(results) >= max_results:
            break
        title = o.get("title") or "Untitled"
        snippet = o.get("snippet") or ""
        link = o.get("link") or ""
        text = snippet.strip() or (f"See: {link}" if link else "")
        results.append({"source": link or f"serpapi:{title}", "title": title, "text": text})

    # pad with placeholders if we didn't get enough
    while len(results) < max_results:
        results.append({"source": "serpapi:placeholder", "title": "No result", "text": "No web result available."})

    return results


def wikipedia_search(query: str, max_results: int = 3) -> List[Dict]:
    """
    Use the wikipedia package to search and return exactly max_results items (with placeholders if needed).
    We fetch more candidates than requested and pick up to max_results successfully retrieved summaries.
    """
    results: List[Dict] = []
    try:
        all_titles = wikipedia.search(query)
    except Exception as e:
        print(f"[wikipedia_search] search error: {e}")
        # return placeholders if search fails
        return [{"source": "wikipedia:placeholder", "title": "No result", "text": "Wikipedia search failed."}
                for _ in range(max_results)]

    # request more candidates to improve chance of getting max_results valid summaries
    max_candidates = max(5, max_results * 4)
    candidates = all_titles[:max_candidates]

    for title in candidates:
        if len(results) >= max_results:
            break
        text = ""
        try:
            text = wikipedia.summary(title, sentences=3)
        except Exception as e1:
            # try fetching page and use summary/content if possible
            try:
                page = wikipedia.page(title, auto_suggest=False)
                text = getattr(page, "summary", "") or (getattr(page, "content", "")[:800])
            except Exception as e2:
                # skip this candidate (we will use more candidates or placeholder later)
                print(f"[wikipedia_search] could not fetch summary/page for '{title}': {e1} | {e2}")
                text = ""

        if text and text.strip():
            results.append({"source": f"wikipedia:{title}", "title": title, "text": text.strip()})
        # else continue to next candidate to try to fill results

    # if still not enough, pad with placeholders so UI receives predictable length
    while len(results) < max_results:
        results.append({"source": "wikipedia:placeholder", "title": "No result", "text": "No Wikipedia result available."})

    return results


def web_retrieve(query: str, max_results: int = 3) -> List[Dict]:
    """
    Top-level web retrieval:
    - Try SerpAPI first (if configured); otherwise fall back to Wikipedia.
    - Guarantee the returned list length equals max_results (using placeholders if necessary).
    """
    # prefer SerpAPI results if available
    serp = serpapi_search(query, max_results=max_results)
    if serp and any(item.get("text") for item in serp):
        return serp[:max_results]

    # otherwise, use Wikipedia
    wiki = wikipedia_search(query, max_results=max_results)
    return wiki[:max_results]

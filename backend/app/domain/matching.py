import re

# Multilingual signals that a message is a problem report / complaint.
# Heuristic only: Milestone 5 adds LLM intent detection; the evaluation will
# measure how well this works.
COMPLAINT_SIGNALS = [
    # English
    "complaint", "complain", "report", "not working", "not collected",
    "not picked", "no water", "not coming", "broken", "blocked", "overflow",
    "leak", "damaged", "stink", "dirty", "there is", "there are", "near my",
    "outside my", "in front of my",
    # Marathi / Hindi
    "तक्रार", "शिकायत", "खराब", "बंद", "तुंबले", "गळती", "येत नाही",
    "उचलला नाही", "नहीं आ रहा", "जाम",
    # Roman script
    "takrar", "shikayat", "kharab",
]


def _hit(keyword: str, low_text: str) -> bool:
    kw = keyword.lower().strip()
    if not kw:
        return False
    if kw.isascii():
        # ASCII: match at a word start ("drain" matches "drains", not "undrained").
        return re.search(r"\b" + re.escape(kw), low_text) is not None
    # Devanagari: \b is unreliable with combining marks, so use substring match.
    return kw in low_text


def count_hits(keywords: list[str], text: str) -> int:
    low = text.lower()
    return sum(1 for k in keywords if _hit(k, low))


def has_complaint_signal(text: str) -> bool:
    return count_hits(COMPLAINT_SIGNALS, text) > 0


def best_topic(topics, text: str, complaint_only: bool = False):
    """Best keyword match. Ties go to the topic listed first in topics.yaml."""
    best, best_hits = None, 0
    for topic in topics:
        if complaint_only and not topic.complaint_enabled:
            continue
        hits = count_hits(topic.keywords, text)
        if hits > best_hits:
            best, best_hits = topic, hits
    return best, best_hits
import random

QUESTION_BANK = [
    {"id": 1, "text": "What did you have for breakfast today?", "domain": "memory"},
    {"id": 2, "text": "Please repeat the phrase: 'Blue river mountain'.", "domain": "language"},
    {"id": 3, "text": "Count backwards from 20 to 1.", "domain": "attention"},
    {"id": 4, "text": "If you had 15 apples and gave away 7, how many remain?", "domain": "executive"},
    {"id": 5, "text": "What day of the week is it today?", "domain": "memory"},
    {"id": 6, "text": "Name as many animals as you can in 30 seconds.", "domain": "language"},
    {"id": 7, "text": "Subtract 7 from 100 repeatedly (say first three results).", "domain": "attention"},
    {"id": 8, "text": "Plan: You have a doctor visit at 3 PM and a bus at 2:40 PM. What do you do?", "domain": "executive"},
]

DOMAIN_LIST = ["memory", "language", "attention", "executive"]

def score_response(domain: str, response: str) -> float:
    if not response or len(response.strip()) < 3:
        return 0.2
    if domain == "attention" and any(ch.isdigit() for ch in response):
        return 0.8
    if domain == "executive" and any(d in response for d in ["8", "eight", "bus", "plan", "reschedule"]):
        return 0.8
    if domain == "language" and len(response.split()) >= 3:
        return 0.7
    if domain == "memory" and any(w in response.lower() for w in ["today", "yesterday", "breakfast"]):
        return 0.7
    return 0.6

def aggregate_domain_scores(history):
    totals = {d: [] for d in DOMAIN_LIST}
    for item in history:
        if item.get('domain') in totals:
            totals[item['domain']].append(item.get('score', 0.0))
    return {k: (sum(v)/len(v) if v else 0.0) for k, v in totals.items()}

def _asked_ids(history):
    return set(h.get("qid") for h in history if "qid" in h)

def _domain_counts(history):
    counts = {d: 0 for d in DOMAIN_LIST}
    for h in history:
        d = h.get("domain")
        if d in counts:
            counts[d] += 1
    return counts

def next_question(history, max_per_domain=2):
    """Pick a non-repeated question, preferring the weakest domain,
    and limiting to max_per_domain per domain. Returns a dict or None if exhausted."""
    asked = _asked_ids(history)
    domain_scores = aggregate_domain_scores(history)
    print("domain_scores==",domain_scores)
    # Compute how many asked per domain
    counts = _domain_counts(history)
    print("counts==",counts)
    # Domains sorted by ascending score, then by having capacity remaining
    domains_sorted = sorted(DOMAIN_LIST, key=lambda d: (domain_scores.get(d, 0.0), counts.get(d, 0)))
    for dom in domains_sorted:
        if counts.get(dom, 0) >= max_per_domain:
            continue
        candidates = [q for q in QUESTION_BANK if q["domain"] == dom and q["id"] not in asked]
        if candidates:
            return random.choice(candidates)
    # If all domains reached their cap, return None to signal completion
    return None

from .prompt_optimizer import optimize_text
from .reporting import handle_reporting
from .cyber_analyzer import analyze_message

from django.core.cache import cache
from difflib import SequenceMatcher

import hashlib
import time
import tiktoken

SECURE_PROMPT = """
You are CyberSafe AI, a cybersecurity assistant for India.

Give simple, latest and clear advice in plain text like a normal chat(no markdown or symbols).
Focus on prevention, threats, and safe practices.
Mention Indian context when relevant (e.g., IT Act, cybercrime.gov.in).
Do not suggest unofficial reporting sites.

Keep it short (max 80 words) and end with a brief conclusion.
"""

EMERGENCY_PROMPT = """
You are CyberSafe AI emergency assistant for India.

User may be under attack. Give urgent, direct steps in plain text(no markdown or symbols).
Focus on safety, damage control, and immediate actions.
If needed, guide to cybercrime.gov.in or helpline 1930.

Keep it very short (max 60 words).
"""

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(enc.encode(text))

def normalize(text):
    return " ".join(sorted(text.lower().split()))

def generate_cache_key(mode, optimized_input,category):
    normalized = normalize(optimized_input)
    key = f"{mode}:{normalized}:{category}"
    return hashlib.md5(key.encode()).hexdigest()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def build_prompt(mode, message, context):

    context_text = "\n".join(context)

    if mode == "emergency_response":
        return f"""{EMERGENCY_PROMPT}

Recent context:
{context_text}

User: {message}
"""

    return f"""{SECURE_PROMPT}

Recent context:
{context_text}

User: {message}
"""

def is_allowed(message):

    blocked = [
        "how to hack",
        "how to attack",
        "ddos guide"
    ]

    for word in blocked:
        if word in message.lower():
            return False

    return True

def clean_output(text):
    return text.strip().replace("\n\n\n", "\n\n")

def orchestrate(request, message, generate_fn):

    if not message.strip():
        return "Please enter a valid message.", None, "unknown"

    current_mode = request.session.get("mode")
    current_category = request.session.get("category", "unknown")

    history = request.session.get("history", [])
    front_history = request.session.get("front_history", [])

    category = current_category

    if request.session.get("post_emergency"):

        msg = message.lower().strip()

        positive_responses = [
            "yes",
            "yeah",
            "yep",
            "ok",
            "sure"
        ]
        negative = ["no", "nah", "later"]

        if any(word in msg for word in positive_responses) or "report" in msg:

            request.session["post_emergency"] = False
            request.session["mode"] = "incident_reporting"

            request.session.pop("report", None)
            request.session.modified = True

            return (
                handle_reporting(request, ""),
                "incident_reporting",
                category
            )
        elif any(word in msg for word in negative):
            request.session["post_emergency"] = False
            request.session.modified = True

        else:
            request.session["post_emergency"] = False
            request.session.modified = True

    # If already in reporting → continue

    if current_mode == "incident_reporting":

        report = request.session.get("report")

        if report and not report.get("completed"):

            return (
                handle_reporting(request, message),
                "incident_reporting",
                category
            )

        # finished → exit reporting

        request.session["mode"] = None
        request.session.pop("report", None)

        request.session.modified = True

        current_mode = None

    analysis = analyze_message(message, history)

    mode = analysis["mode"]
    new_category = analysis["category"]

    if new_category != "unknown":
        category = new_category

    if current_mode == "incident_reporting":

        # allow exit OR strong emergency override only

        if mode == "emergency_response":

            request.session["mode"] = "emergency_response"

            request.session.pop("report", None)
            request.session.modified = True

        else:
            mode = "incident_reporting"

    # Start reporting if detected

    if mode == "incident_reporting":

        request.session["mode"] = "incident_reporting"

        request.session.pop("report", None)

        request.session.modified = True

        return (
            handle_reporting(request, message),
            "incident_reporting",
            category
        )

    # normal flow

    request.session["mode"] = mode
    request.session["category"] = category

    request.session.modified = True

    # optimize input using spacy

    optimized_input = optimize_text(message)
    optimized_input = optimized_input.strip().lower()

    # Create cache key

    cache_key = generate_cache_key(mode, optimized_input, category)

    # Check cache first

    # 1. Exact match

    cached = cache.get(cache_key)

    if cached:

        print("CACHE HIT (exact)")

        # Update LRU

        all_inputs = cache.get("all_inputs") or []

        for item in all_inputs:
            if item["key"] == cache_key:
                item["last_used"] = time.time()

        cache.set("all_inputs", all_inputs, timeout=None)

        return cached["reply"], mode, category

    # 2. Similarity search

    all_inputs = cache.get("all_inputs") or []

    best_match = None
    best_score = 0

    for item in all_inputs:

        score = similarity(
            normalize(optimized_input),
            normalize(item["input"])
        )

        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score > 0.65:

        cached = cache.get(best_match["key"])

        if cached:

            print(f"CACHE HIT (similarity {best_score:.2f})")

            # Update LRU

            for item in all_inputs:
                if item["key"] == best_match["key"]:
                    item["last_used"] = time.time()

            cache.set("all_inputs", all_inputs, timeout=None)

            return cached["reply"], mode, category

    print("CACHE MISS")

    # get context

    context = history[-5:]

    # build prompt

    prompt = build_prompt(mode, message, context)

    # generate response if cache miss

    reply = clean_output(generate_fn(prompt))

    if mode == "emergency_response":

        reply += " Do you want help filing a complaint?"

        request.session["post_emergency"] = True

    # store in global cache

    cache.set(
        cache_key,
        {
            "input": optimized_input,
            "reply": reply
        },
        timeout=3600
    )

    all_inputs = cache.get("all_inputs") or []

    exists = False

    for item in all_inputs:

        if item["input"] == optimized_input:

            item["last_used"] = time.time()

            exists = True
            break

    if not exists:

        all_inputs.append({
            "key": cache_key,
            "input": optimized_input,
            "last_used": time.time()
        })

    # LRU eviction

    if len(all_inputs) > 1000:

        all_inputs = sorted(
            all_inputs,
            key=lambda x: x["last_used"]
        )

        all_inputs = all_inputs[-1000:]

    cache.set("all_inputs", all_inputs, timeout=None)

    history.append(f"User: {optimized_input}")
    history.append(f"Bot: {reply}")

    front_history.append({
        "role": "user",
        "text": message
    })

    front_history.append({
        "role": "bot",
        "text": reply
    })

    request.session["history"] = history[-10:]
    request.session["front_history"] = front_history[-20:]

    request.session.modified = True

    return reply, mode, category
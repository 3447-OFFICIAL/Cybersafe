from collections import defaultdict
from .preprocess import preprocess_text

def context_classification(history,classifier_function,limit=5, confidence_threshold = 0.6):
    if not history:
        return None
    scores= defaultdict(float)
    recent_messages=[]

    for item in reversed(history):
        if item.startswith("User:"):
            msg =item.replace("User:","").strip()
            if msg:
                recent_messages.append(msg)
        if len(recent_messages)>= limit:
            break

    recent_messages.reverse()

    for msg in recent_messages:
        cleaned = preprocess_text(msg)
        result = classifier_function(cleaned)

        category = result["category"]
        confidence = result["category_confidence"]

        print("MESSAGE:", msg)
        print("CATEGORY:", category)
        print("CONFIDENCE:", confidence)


        if category == "unknown":
            continue

        if confidence < confidence_threshold:
            continue

        scores[category] += confidence
    if not scores:
        return None
    best_category = max(scores, key=scores.get)

    print("\n====== CONTEXT ENGINE ======")

    for item in recent_messages:
        print("MESSAGE:", item)
        print("CATEGORY:", category)
        print("CONFIDENCE:", confidence)

    return best_category
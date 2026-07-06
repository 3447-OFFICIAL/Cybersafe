try:
    import spacy
    try:
        nlp = spacy.load(
            "en_core_web_sm",
            disable=["parser", "ner", "lemmatizer"]
        )
    except Exception:
        nlp = spacy.blank("en")
except ImportError:
    nlp = None

def optimize_text(text):
    if not nlp:
        # Fallback simple text cleaner if spacy is not installed
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        return " ".join(tokens)

    doc = nlp(text)

    important_pos = {'NOUN','VERB','PROPN','NUM'}

    tokens =[
        token.text.lower()
        for token in doc
        if token.pos_ in important_pos and not token.is_punct
        or (token.pos_ == 'ADJ' and not token.is_stop)
    ]
    return " ".join(tokens)
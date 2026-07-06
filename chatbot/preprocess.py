try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = spacy.blank("en")
except ImportError:
    nlp = None
    
def preprocess_text(text):
    if not nlp:
        # Fallback simple regex word extractor if spacy is not installed
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        return " ".join(tokens)

    doc = nlp(text.lower())
    cleaned_tokens=[]

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue
        cleaned_tokens.append(token.lemma_)

    return " ".join(cleaned_tokens)

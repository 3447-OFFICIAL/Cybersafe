import logging
from .preprocess import preprocess_text
from .context_engine import context_classification

logger = logging.getLogger(__name__)

# Lazy model loaders
_model_mode = None
_vectorizer_mode = None
_model_cat = None
_vectorizer_cat = None
_models_loaded = False

def load_ml_models():
    global _model_mode, _vectorizer_mode, _model_cat, _vectorizer_cat, _models_loaded
    if _models_loaded:
        return True
    try:
        import joblib
        _model_mode = joblib.load("chatbot/ml/model_mode.pkl")
        _vectorizer_mode = joblib.load("chatbot/ml/vectorizer_mode.pkl")
        _model_cat = joblib.load("chatbot/ml/model_categories.pkl")
        _vectorizer_cat = joblib.load("chatbot/ml/vectorizer_categories.pkl")
        _models_loaded = True
        logger.info("Chatbot machine learning models loaded successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to load machine learning models: {e}. Falling back to default heuristics.")
        return False

def classify_category_only(message):
    if not load_ml_models():
        return {
            "category": "unknown",
            "category_confidence": 0.0
        }
    try:
        vector = _vectorizer_cat.transform([message])
        prediction = _model_cat.predict(vector)[0]
        probabilities = _model_cat.predict_proba(vector)[0]
        confidence = max(probabilities)
        return {
            "category": prediction,
            "category_confidence": confidence
        }
    except Exception as e:
        logger.error(f"ML classification runtime error: {e}")
        return {
            "category": "unknown",
            "category_confidence": 0.0
        }

# analyser function

def analyze_message(message, history = None):
    cleaned_input = preprocess_text(message)
    hist = 0

    if not load_ml_models():
        # Fallback heuristic: simple rule-based analysis
        mode_prediction = "security_guidance"
        mode_confidence = 1.0
        category_prediction = "unknown"
        category_confidence = 1.0
    else:
        try:
            mode_vector = _vectorizer_mode.transform([cleaned_input])
            mode_prediction = _model_mode.predict(mode_vector)[0]
            mode_probabilities = _model_mode.predict_proba(mode_vector)[0]
            mode_confidence = max(mode_probabilities)

            category_vector = _vectorizer_cat.transform([cleaned_input])
            category_prediction = _model_cat.predict(category_vector)[0]
            category_probabilities = _model_cat.predict_proba(category_vector)[0]
            category_confidence = max(category_probabilities)
        except Exception as err:
            logger.error(f"ML analysis runtime error: {err}")
            mode_prediction = "security_guidance"
            mode_confidence = 1.0
            category_prediction = "unknown"
            category_confidence = 1.0

    if (category_prediction == "unknown" or category_confidence < 0.55):
        contextual_category = context_classification(history, classify_category_only)

        if contextual_category:
            category_prediction = contextual_category
            hist = 1

    print("\n========== ANALYSIS ==========")
    print("MESSAGE:", message)

    print("\nMODE:")
    print(mode_prediction)
    print(mode_confidence)

    print("\nCATEGORY:")
    print(category_prediction)
    print(category_confidence)

    if category_confidence < 0.50 and hist != 1:
        category_prediction = "unknown"
    
    if mode_confidence < 0.55:
        mode_prediction = "security_guidance"

    return {
        "mode": mode_prediction,
        "mode_confidence": round(float(mode_confidence), 4),

        "category": category_prediction,
        "category_confidence": round(float(category_confidence), 4)
    }
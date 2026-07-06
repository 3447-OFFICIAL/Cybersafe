import json
from django.http import JsonResponse
from .gemini_client import generate
from .orchestrator import orchestrate
from .session_manager import get_session_id
from django.views.decorators.csrf import ensure_csrf_cookie
import tiktoken
from django.shortcuts import render

def home(request):
    return render(request, "index.html")

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(enc.encode(text))

@ensure_csrf_cookie
def reset_chat(request):

    request.session.flush()

    return JsonResponse({
        "status": "reset successful"
    })

@ensure_csrf_cookie
def get_history(request):

    front_history = request.session.get("front_history", [])

    return JsonResponse({
        "history": front_history,
        "mode": request.session.get("mode")
    })

@ensure_csrf_cookie
def chat(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    body = json.loads(request.body)
    message = body.get("message", "")

    session_id = get_session_id(request)

    reply, mode, category = orchestrate(request, message, generate)

    # token counting
    input_tokens = count_tokens(message)
    output_tokens = count_tokens(reply)
    total_tokens = input_tokens + output_tokens

    return JsonResponse({
        "response": reply,
        "mode": mode,
        "category": category,
        "session_id": session_id,
        "tokens": {
            "input": input_tokens,
            "output": output_tokens,
            "total": total_tokens
        }
    })
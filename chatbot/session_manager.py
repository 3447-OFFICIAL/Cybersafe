def get_session_id(request):
    session_id = request.session.session_key
    
    if not session_id:
        request.session.create()
        session_id=request.session.session_key

    return session_id

def init_session(request):
    if "mode" not in request.session:
        request.session["mode"] ="secure"

    if "history" not in request.session:
        request.session["history"] =[]
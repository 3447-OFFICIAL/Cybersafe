from .gemini_client import generate

def format_report_summary(data):
    return (
        f"Please review your details:\n\n"
        f"Incident: {data['incident']}\n"
        f"Date: {data['date']}\n"
        f"Platform: {data['platform']}\n"
        f"Loss: {data['loss']}\n"
        f"Transaction ID: {data['transaction_id']}\n"
        f"Scammer Info: {data['scammer']}\n"
        f"Evidence: {data['evidence']}\n\n"
        f"Type 'confirm' if everything is correct.\n"
        f"Or type the field name to edit (e.g., 'loss', 'platform')."
    )

# prompt for gemini reporting

def build_report_prompt(data):
    return f"""
You are CyberSafe AI helping draft a formal cybercrime complaint for India.

Write a clear, professional complaint using the details below in chronological order. Use plain text only, no formatting or symbols. Do not add any extra or fake details. Keep it concise but complete.

Details:
Incident: {data['incident']}
Date: {data['date']}
Platform: {data['platform']}
Loss: {data['loss']}
Transaction ID: {data['transaction_id']}
Scammer Details: {data['scammer']}
Evidence: {data['evidence']}

Return only the complaint text.
"""

def step_incident(request, message):
    if not message.strip():
        return "What exactly happened?"
    report = request.session["report"]

    report["data"]["incident"] = message
    report["step"] = 2

    request.session.modified = True
    return "When did this happen?"

def step_urgency(request, message):
    report = request.session["report"]
    report["current_field"] = "platform"

    msg = message.lower()

    # Simple urgency detection
    critical_keywords = [
        "just now", "minutes ago", "right now", "few minutes",
        "today", "recent", "immediately"
    ]

    is_critical = any(word in msg for word in critical_keywords)

    # store time info
    report["data"]["date"] = message

    if is_critical:
        report["urgency"] = "critical"
        report["step"] = 3   # go to urgent action
        request.session.modified = True

        return (
            "This just happened — you are in the golden hour.\n\n"
            "Call 1930 immediately to try freezing the money.\n"
            "Tell them: 'Unauthorized transaction, request immediate block'\n\n"
            "Type 'done' after you have called."
        )

    else:
        report["urgency"] = "normal"
        report["step"] = 4   # skip urgent step
        request.session.modified = True

        return "Which platform was involved? (UPI / bank / email / whatsapp)"

def step_urgent_action(request, message):
    report = request.session["report"]

    if "done" in message.lower():
        report["step"] = 4
        request.session.modified = True

        return "Good. Now tell me — which platform was involved? (UPI / bank / email / whatsapp)"

    return "Please call 1930 first. Type 'done' once completed."

def step_collect_details(request, message):
    report = request.session["report"]
    data = report["data"]
    current = report.get("current_field", "platform")

    field_order = [
        "platform",
        "loss",
        "transaction_id",
        "scammer",
        "evidence"
    ]

    questions = {
        "platform": "Which platform was involved? (UPI / bank / email / whatsapp)",
        "loss": "How much money was lost? (if none, type 0)",
        "transaction_id": "Do you have the transaction ID (UTR)?",
        "scammer": "Do you have scammer details? (phone / UPI / account)",
        "evidence": "Do you have any evidence? (screenshots, messages, call logs)"
    }

    # store previous answer
    if current and data[current] is None and message.strip():
        data[current] = message

    # find next field
    current_index = field_order.index(current)

    if current_index + 1 < len(field_order):
        next_field = field_order[current_index + 1]
        report["current_field"] = next_field
        request.session.modified = True
        return questions[next_field]

    # all collected
    report["step"] = 5
    request.session.modified = True

    return "Thanks. Let me quickly verify your information."

def step_validation(request, message):
    report = request.session["report"]
    data = report["data"]

    # FIRST ENTRY → show summary
    if not report.get("validation_shown"):
        report["validation_shown"] = True
        request.session.modified = True
        return format_report_summary(data)

    msg = message.lower().strip()

    # CONFIRM
    if msg == "confirm":
        report["step"] = 6
        request.session.modified = True
        return "Generating your complaint..."

    # EDIT FIELD
    editable_fields = [
        "incident", "date", "platform",
        "loss", "transaction_id", "scammer", "evidence"
    ]

    # HANDLE UPDATED VALUE FIRST
    if report.get("edit_field"):
        field = report["edit_field"]
        report["validation_shown"] = True
        data[field] = message.strip()
        report["edit_field"] = None
        report["validation_shown"] = False
        request.session.modified = True

        return format_report_summary(data)

    # THEN check for edit request
    if msg in editable_fields:
        report["edit_field"] = msg
        report["validation_shown"] = False
        request.session.modified = True
        return f"Enter the correct value for {msg}:"
    return "Please type 'confirm' or a valid field name to edit."

def step_generate_report(request, message):
    report = request.session["report"]
    data = report["data"]

    # prevent regeneration on every message
    if not report.get("generated_report"):

        prompt = build_report_prompt(data)

        # call your existing generate()
        try:
            generated_text = generate(prompt)
        except Exception:
            report["step"] = 5   # go back to validation
            request.session.modified = True
            return "Failed to generate report. Please try again."
        
        report["generated_report"] = generated_text
        report["step"] = 7

        request.session.modified = True

        return (
            "Here is your complaint draft:\n\n"
            f"{generated_text}\n\n"
            "Type 'ok' to proceed to submission guidance."
        )

    # waiting for confirmation
    if "ok" in message.lower():
        return step_guidance(request, message)

    return "Type 'ok' when you are ready to proceed."

def step_guidance(request, message):
    report = request.session["report"]
    step = report.get("guide_step", 1)

    # STEP 1
    if step == 1:
        report["guide_step"] = 2
        request.session.modified = True

        return (
            "Open https://cybercrime.gov.in in a new tab.\n\n"
            "Type 'done' when the website is open."
        )

    # STEP 2
    elif step == 2:
        if "done" in message.lower():
            report["guide_step"] = 3
            request.session.modified = True

            return (
                "Click on 'Report & Track'.\n\n"
                "Type 'done' when you see the complaint page."
            )
        return "Please open the website and type 'done'."

    # STEP 3
    elif step == 3:
        if "done" in message.lower():
            report["guide_step"] = 4
            request.session.modified = True
            return (
                "Good. Now select the appropriate category (Financial Fraud / Other).\n\n"
                "Then proceed to fill in your details.\n"
                "Type 'done' once ready."
            )
        return "Select the category and type 'done'."

    # STEP 4 → Fill form
    elif step == 4:
        if "done" in message.lower():
            report["guide_step"] = 5
            request.session.modified = True
            return (
                "Now upload your evidence (screenshots, messages, call logs).\n\n"
                "Type 'done' once uploaded."
            )
        return (
            "Now fill in your details using the complaint I generated.\n\n"
            "Paste the description in the 'Complaint Details' section.\n"
            "Type 'done' when finished."
        )


    # STEP 5 → Upload evidence
    elif step == 5:
        if "done" in message.lower():
            report["guide_step"] = 6
            request.session.modified = True
            return (
                "Submit the complaint.\n\n"
                "After submission, you will receive an acknowledgement number.\n"
                "Type 'done' once submitted."
            )
        return "Upload your evidence and type 'done'."


    # STEP 6 → Submit confirmation
    elif step == 6:
        if "done" in message.lower():
            report["guide_step"] = 7
            request.session.modified = True
            return (
                "Finalizing your complaint...\n\n"
                "Processing..."
            )
        return "Please submit the complaint and type 'done'."
    # FINAL
    elif step == 7:
        report["completed"] = True
        request.session.modified = True

        return (
            "Your complaint has been submitted successfully.\n\n"
            "You can track it using your acknowledgement number.\n\n"
            "Type 'report' if you want to file another complaint."
        )
    return "Continue with the steps and type 'done' when ready."


def handle_reporting(request, message):
    
    if message.lower() in ["exit", "cancel"]:
        request.session.pop("report", None)
        return "Reporting cancelled. How else can I help you?"

    # Initialize session
    if "report" not in request.session:
        request.session["report"] = {
            "step": 1,
            "data": {
                "incident": None,
                "date": None,
                "platform": None,
                "loss": None,
                "scammer": None,
                "evidence": None,
                "transaction_id": None
            },
            "urgency": None,
            "current_field": "platform",
            "completed": False,
            "validation_shown": False,
            "edit_field": None,
            "generated_report": None,
            "guide_step": 1
        }

    report = request.session["report"]
    step = report["step"]

    if report.get("completed"):
        request.session.pop("report", None)
        request.session["mode"] = None
        request.session.modified = True
        return None
    # STEP 1 → INCIDENT
    if step == 1:
        return step_incident(request, message)
    # STEP 2 → URGENCY
    elif step == 2:
        return step_urgency(request, message)

    # STEP 3 → URGENT ACTION
    elif step == 3:
        return step_urgent_action(request, message)

    # STEP 4 → DETAILS COLLECTION
    elif step == 4:
        return step_collect_details(request, message)

    # STEP 5 → VALIDATION
    elif step == 5:
        return step_validation(request, message)

    # STEP 6 → GENERATE REPORT
    elif step == 6:
        return step_generate_report(request, message)

    # STEP 7 → GUIDANCE
    elif step == 7:
        return step_guidance(request, message)

# fallback
    else:
        report["completed"] = True
        request.session["mode"] = None
        return "Something went wrong. Please restart reporting."
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text):
    return model.encode(text)

def sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ============================================================
# EMERGENCY MODE - Victim needing immediate help (20 examples)
# ============================================================

emergency_examples = [
    # Hacking - past tense
    "my account got hacked",
    "someone hacked my Instagram",
    "I've been hacked",
    "someone accessed my account without permission",
    
    # Scams - victim language
    "I got scammed",
    "I was scammed on UPI",
    "someone scammed me out of money",
    "I fell for a scam",

    # Malware / ransomware
    "my files got locked",
    "i cannot access my files",
    "my device got infected",
    "i downloaded malware",
    "my computer has ransomware",
    "all my files are encrypted",
    "my laptop got hacked",
    "i opened a malicious file",
    "virus infected my computer",
    "suspicious popup appeared",
    "my system is compromised",
    "i clicked a fake lottery popup",
    
    # Money loss - urgent
    "money was stolen from my account",
    "unauthorized transaction just happened",
    "my money is gone",
    "someone took my money",
    
    # Phishing/Data breach
    "I clicked a suspicious link",
    "I gave my OTP to someone by mistake",
    "I shared my password with a scammer",
    "I entered my details on a fake website",
    
    # Urgency
    "this just happened",
    "what should I do right now",
    "need urgent help",
    "how do I stop this immediately",
    
    # SIM swapping
    "my phone suddenly has no signal",
    "I can't make calls but my phone works",
    "my SIM card shows no service",
    "someone ported my number",
    "calls are going to someone else's phone",
    "my mobile number was transferred without permission",
    
    # Account takeover
    "I can't log into my email anymore",
    "my password suddenly doesn't work",
    "password was changed and I didn't do it",
    "locked out of my Facebook account",
    "someone changed my recovery email",
    "got logged out of all devices",
    "my account password was reset by someone else",
    
    # Credential stuffing
    "getting alerts about login attempts from different countries",
    "someone is trying to access my accounts",
    "multiple failed login notifications",
    "unusual login activity detected",
    
    # Social engineering calls
    "bank called asking me to verify my card details",
    "someone from tech support called about a virus",
    "got a call from 'Microsoft' about my computer",
    "caller ID showed my bank's name",
    "someone called saying my account will be blocked",
    "received call asking for OTP",
    
    # Investment scams
    "invested in cryptocurrency and can't withdraw",
    "trading platform locked my funds",
    "forex broker won't let me take my money out",
    "invested in scheme that seems fake now",
    "promised high returns but can't access money",
    "crypto investment site disappeared",
    "put money in trading app that stopped working",
    
    # Romance scams
    "met someone online who keeps asking for money",
    "person I'm dating needs emergency funds",
    "online relationship asking for gift cards",
    "sent money to someone I met on dating app",
    
    # Job scams
    "paid training fee for job that doesn't exist",
    "work from home company took my money and vanished",
    "job offer asking me to pay upfront",
    "received check to deposit for fake job",
    "asked to buy equipment for remote job",
    
    # Refund scams
    "call about refund I need to claim urgently",
    "someone says I'm owed money from government",
    "email about tax refund with link",
    "message about unclaimed package refund",
    
    # Vishing
    "got automated call about arrest warrant",
    "call from fraud department asking to verify account",
    "someone called saying my Aadhaar is suspended",
    "recorded message about legal action against me",
    "call threatening police action if I don't pay",
    "someone called about suspicious activity on card",
    
    # Doxxing
    "my personal information was posted online",
    "someone leaked my address publicly",
    "my phone number is on a public forum",
    "private details shared without consent",
    "found my home address on a website",
    
    # Sextortion
    "someone has private photos of me",
    "threatening to share intimate content",
    "blackmail with compromising videos",
    "someone recorded me on video chat",
    "extortion with personal images",
    
    # Stalkerware/spyware
    "someone is tracking my location",
    "I think my phone is being monitored",
    "my messages are being read by someone",
    "partner installed tracking app",
    "location shows up places I haven't been",
    "someone knows things they shouldn't",
    
    # Webcam hijacking
    "webcam light turns on by itself",
    "camera activating when not in use",
    "laptop camera seems to be accessed",
    "indicator light on when no apps open",
    
    # Cryptojacking
    "my computer is really slow suddenly",
    "device overheating for no reason",
    "high CPU usage but nothing running",
    "battery draining extremely fast",
    "fan running constantly",
    "phone getting hot while idle",
    
    # Man-in-the-middle
    "getting security warnings on websites",
    "certificate error on familiar sites",
    "used public WiFi and now having issues",
    "browser shows 'not secure' on banking site",
    "SSL certificate doesn't match",
    
    # IoT compromise
    "my smart camera is acting weird",
    "someone accessed my security camera",
    "smart lock unlocked by itself",
    "Ring doorbell footage seems accessed",
    "smart TV showing strange content",
    "Alexa responding to commands I didn't give",
    
    # Juice jacking
    "charged my phone at airport USB port",
    "used public charging station",
    "plugged into unknown USB port",
    "phone acting strange after public charging",
    
    # Smishing
    "text about package delivery with suspicious link",
    "SMS saying my account will be suspended",
    "message from bank asking to click link",
    "text about winning a prize",
    "SMS with tracking link for delivery",
    "message saying verify account or lose access",
    "text with shortened URL about payment",
    
    # Deepfake
    "video call with family member seemed off",
    "received voice message that sounds wrong",
    "boss's video message seems fake",
    "voice call from relative asking for money sounded strange",
    
    # Impersonation
    "someone created fake profile with my photos",
    "imposter using my name online",
    "fake account pretending to be me",
    "someone messaging my friends as me",
    "duplicate profile of me exists",
    
    # Business email compromise
    "boss sent unusual payment request email",
    "CEO asking to buy gift cards urgently",
    "email from manager to transfer funds looks suspicious",
    "vendor changed bank details suddenly",
    "urgent wire transfer request from executive",
    
    # Accidental deletion
    "I permanently deleted important files",
    "emptied recycle bin by mistake",
    "formatted drive accidentally",
    "lost all photos from phone",
    
    # Cloud account locked
    "Google locked me out of my account",
    "can't access my iCloud",
    "Microsoft account suspended",
    "Dropbox won't let me log in",
    "lost access to cloud storage",
    
    # Backup failure
    "backup wasn't running and now files lost",
    "external drive failed, no other backup",
    "cloud backup didn't sync",
    "Time Machine backup corrupted",
    
    # Fake apps
    "downloaded banking app that looks slightly different",
    "app asking for unusual permissions",
    "installed app from third-party store",
    "PayTM-like app but not official",
    "WhatsApp clone asking for contacts",
    
    # Update scams
    "popup says Flash Player needs update",
    "browser showing update required message",
    "website forcing me to install update",
    "fake Adobe update notification",
    
    # Trojanized software
    "downloaded cracked Photoshop",
    "installed pirated Windows",
    "used key generator for software",
    "downloaded movie that was actually .exe file",
    "torrent file infected my computer",
    
    # Browser hijacking
    "my homepage changed to unknown site",
    "search engine keeps redirecting",
    "browser opens ads automatically",
    "new toolbar appeared in browser",
    "default search changed without permission",
    
    # AI voice cloning
    "got call from family member asking for emergency money but voice sounded slightly off",
    "voice message from boss sounds almost right",
    "call claiming to be from relative in trouble",
    "voice sounded like my child asking for help",
    
    # QR code scams
    "scanned QR code and money was deducted",
    "QR code for menu charged my account",
    "parking QR code took payment",
    "scanned code at restaurant, got charged extra",
    
    # Fake booking sites
    "hotel reservation turned out to be fake",
    "booked flight on lookalike website",
    "Airbnb listing doesn't exist",
    "paid for accommodation that wasn't real",
    "travel booking site took money and disappeared",
    
    # Pump and dump
    "cryptocurrency I bought crashed immediately",
    "influencer recommended coin that tanked",
    "Telegram group pumped coin then it collapsed",
    "bought token that lost all value overnight",
]

# ============================================================
# REPORTING MODE - Want to file complaint (15 examples)
# ============================================================

reporting_examples = [
    # Direct intent
    "how do I file a complaint",
    "I want to report this scam",
    "I need to file a cybercrime complaint",
    "where can I lodge an FIR",
    
    # Process guidance
    "how to report to police",
    "help me submit a complaint",
    "guide me through filing a report",
    "how to file on cybercrime portal",
    
    # Specific platforms
    "how to report to cybercrime.gov.in",
    "I want to register a case online",
    "need help filing police complaint",
    
    # Action-oriented
    "I want to take legal action",
    "how do I formally report this",
    "need to document this fraud",
    "want to file an official complaint",
]

# precompute ONCE
reporting_embeds = [embed(x) for x in reporting_examples]
emergency_embeds = [embed(x) for x in emergency_examples]


def detect_mode(message):
    msg = message.lower().strip()

    # Strong keyword override (highest priority for demo reliability)
    # if any(k in msg for k in ["report", "complaint", "file a case", "lodge"]):
    #     return "reporting"

    # if any(k in msg for k in ["scam", "lost money", "fraud", "fake website"]):
    #     return "reporting"

    # if any(k in msg for k in ["hacked", "urgent", "right now", "just happened", "stolen"]):
    #     return "emergency"

    try:
        # Vector similarity
        msg_emb = embed(message)

        report_score = max(sim(msg_emb, e) for e in reporting_embeds)
        emergency_score = max(sim(msg_emb, e) for e in emergency_embeds)

        # Keyword boosting (soft influence, not override)
        report_keywords = ["report", "file", "complaint", "how to", "fir"]
        emergency_keywords = ["got", "was", "just", "help", "stolen", "hacked"]

        report_boost = sum(0.1 for kw in report_keywords if kw in msg)
        emergency_boost = sum(0.1 for kw in emergency_keywords if kw in msg)

        final_report = report_score + report_boost
        final_emergency = emergency_score + emergency_boost

        print(f"REPORT: {final_report:.3f}")
        print(f"EMERGENCY: {final_emergency:.3f}")

        # Decision logic
        if final_emergency > 0.7 and final_emergency > final_report:
            return "emergency"

        if final_report > 0.65:
            return "reporting"

    except Exception:
        pass  # fallback below

    return "secure"
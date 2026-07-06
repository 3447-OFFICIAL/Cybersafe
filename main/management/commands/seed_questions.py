from django.core.management.base import BaseCommand
from main.models import SecurityQuestion
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seeds the database with standard Security Assessment questions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-seeding by deleting all existing questions first',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # Prevent duplicate seeding unless --force is specified
        if SecurityQuestion.objects.exists() and not force:
            self.stdout.write(self.style.WARNING(
                'Security questions already exist in the database. Seeding skipped. '
                'Run with --force to clear existing questions and re-seed.'
            ))
            return

        self.stdout.write('Seeding security questions...')
        if force:
            self.stdout.write('Clearing existing SecurityQuestion data due to --force flag...')
            SecurityQuestion.objects.all().delete()

        questions_data = [
            # Password Security
            {
                "category": "password_security",
                "text": "What is the primary benefit of using a password manager?",
                "options": ["It prevents you from forgetting your usernames", "It encrypts and stores complex, unique passwords for every site", "It automatically changes your passwords every day", "It stops hackers from guessing your network IP"],
                "correct_option": "B",
                "explanation": "Password managers generate, encrypt, and securely store unique passwords for every service, reducing the risk of credential stuffing.",
                "difficulty": "easy"
            },
            {
                "category": "password_security",
                "text": "Which password is the most secure against brute-force attacks?",
                "options": ["P@ssw0rd123!", "ILoveMyDogRover2023", "B7#k9$mQ2!pL5vX", "Admin123456"],
                "correct_option": "C",
                "explanation": "A completely random string of upper/lowercase letters, numbers, and symbols is mathematically the hardest to brute-force.",
                "difficulty": "medium"
            },
            {
                "category": "password_security",
                "text": "What is 'credential stuffing'?",
                "options": ["Filling out multiple login forms quickly", "Using stolen usernames and passwords from one breach to log into other services", "Guessing passwords using a dictionary of common words", "Creating fake credentials to test security systems"],
                "correct_option": "B",
                "explanation": "Credential stuffing uses automated scripts to try compromised username/password pairs across multiple websites.",
                "difficulty": "medium"
            },
            {
                "category": "password_security",
                "text": "Why is SMS-based Two-Factor Authentication (2FA) considered less secure than an authenticator app?",
                "options": ["SMS messages cost money", "SMS relies on cellular networks which can be intercepted or bypassed via SIM swapping", "Authenticator apps use shorter codes", "SMS messages expire faster"],
                "correct_option": "B",
                "explanation": "SIM swapping or network interception can allow attackers to steal SMS OTPs, whereas authenticator apps generate tokens locally on the device.",
                "difficulty": "hard"
            },
            {
                "category": "password_security",
                "text": "How often should you ideally rotate strong, unique passwords?",
                "options": ["Every 30 days", "Every 90 days", "Every year", "Only when there is a suspected breach or compromise"],
                "correct_option": "D",
                "explanation": "NIST guidelines state that arbitrarily forcing password changes leads to weaker passwords; rotate only upon suspected compromise.",
                "difficulty": "hard"
            },
            # Phishing & Scams
            {
                "category": "phishing",
                "text": "What is 'Spear Phishing'?",
                "options": ["A mass email sent to millions of people", "A targeted phishing attack aimed at a specific individual or organization", "A physical attack on a data center", "A scam involving phone calls"],
                "correct_option": "B",
                "explanation": "Spear phishing uses gathered intelligence to highly personalize an attack against a specific target.",
                "difficulty": "medium"
            },
            {
                "category": "phishing",
                "text": "You receive an urgent email from 'support@paypa1.com' asking you to verify your account. What should you do?",
                "options": ["Click the link and verify", "Reply and ask if it's real", "Ignore it or navigate directly to the official site by typing the URL yourself", "Forward it to all your friends to warn them"],
                "correct_option": "C",
                "explanation": "The domain is misspelled ('paypa1'). Always ignore suspicious links and go directly to the known official website.",
                "difficulty": "easy"
            },
            {
                "category": "phishing",
                "text": "What is the primary indicator of a potentially malicious link in an email?",
                "options": ["It uses HTTPS", "The URL mismatch between the display text and the actual destination", "It contains the word 'secure'", "It is sent on a weekend"],
                "correct_option": "B",
                "explanation": "Hovering over a link often reveals that the actual destination differs entirely from the trusted display text.",
                "difficulty": "medium"
            },
            {
                "category": "phishing",
                "text": "What does a green padlock in the browser address bar guarantee?",
                "options": ["The website is 100% safe and verified", "Your connection to the website is encrypted", "The website cannot contain malware", "The website belongs to a legitimate corporation"],
                "correct_option": "B",
                "explanation": "HTTPS (the padlock) only ensures the connection is encrypted. Phishing sites also use HTTPS.",
                "difficulty": "medium"
            },
            {
                "category": "phishing",
                "text": "What is 'Whaling'?",
                "options": ["Phishing attacks targeting large user databases", "Phishing attacks specifically targeting high-profile executives (CEOs, CFOs)", "Scams involving cryptocurrency investments", "Attacks using large botnets"],
                "correct_option": "B",
                "explanation": "Whaling is a form of spear phishing aimed specifically at high-level executives to gain access to corporate funds or sensitive data.",
                "difficulty": "hard"
            },
            # Social Engineering
            {
                "category": "social_engineering",
                "text": "What is 'Tailgating' in a security context?",
                "options": ["Following closely behind someone's car", "An unauthorized person following an authorized person into a secure building", "Copying someone else's code", "Listening to someone's conversation"],
                "correct_option": "B",
                "explanation": "Tailgating (or piggybacking) occurs when an unauthorized person exploits an authorized person's entry to bypass physical security.",
                "difficulty": "medium"
            },
            {
                "category": "social_engineering",
                "text": "A person calls claiming to be from IT support and asks for your password to 'fix an issue'. What is this an example of?",
                "options": ["Vishing", "Smishing", "Phishing", "Baiting"],
                "correct_option": "A",
                "explanation": "Voice Phishing (Vishing) involves using phone calls to deceive victims into handing over sensitive information.",
                "difficulty": "easy"
            },
            {
                "category": "social_engineering",
                "text": "What is 'Baiting'?",
                "options": ["Sending threatening emails", "Leaving a malware-infected USB drive in a public place hoping someone plugs it in", "Calling posing as a bank", "Spamming comments on social media"],
                "correct_option": "B",
                "explanation": "Baiting relies on human curiosity, like leaving a labeled USB drive in a parking lot to distribute malware.",
                "difficulty": "medium"
            },
            {
                "category": "social_engineering",
                "text": "What psychological trigger is most commonly exploited in social engineering?",
                "options": ["Happiness", "Urgency/Fear", "Boredom", "Sadness"],
                "correct_option": "B",
                "explanation": "Creating a false sense of urgency or fear forces victims to make quick, irrational decisions without verifying facts.",
                "difficulty": "easy"
            },
            {
                "category": "social_engineering",
                "text": "What is 'Pretexting'?",
                "options": ["Writing a fake email subject line", "Creating a fabricated scenario to manipulate someone into divulging information", "Testing security protocols", "Guessing passwords based on text messages"],
                "correct_option": "B",
                "explanation": "Pretexting involves the attacker establishing trust through a highly elaborated lie or persona.",
                "difficulty": "hard"
            },
            # Mobile Security
            {
                "category": "mobile_security",
                "text": "Why should you avoid 'jailbreaking' or 'rooting' your mobile device?",
                "options": ["It deletes all your contacts", "It voids your warranty only", "It bypasses built-in OS security protections and allows apps to access root system files", "It slows down your internet speed"],
                "correct_option": "C",
                "explanation": "Rooting/Jailbreaking removes the sandbox architecture, making the device highly vulnerable to malware.",
                "difficulty": "medium"
            },
            {
                "category": "mobile_security",
                "text": "What is the primary risk of downloading apps from third-party app stores (sideloading)?",
                "options": ["The apps are usually outdated", "The apps are more expensive", "These stores lack strict security scanning, increasing the risk of downloading malware", "They consume too much battery"],
                "correct_option": "C",
                "explanation": "Official stores (Google Play/App Store) scan for malware. Third-party sources often distribute trojanized apps.",
                "difficulty": "easy"
            },
            {
                "category": "mobile_security",
                "text": "What is 'Smishing'?",
                "options": ["Smashing a phone to destroy data", "Phishing attacks conducted via SMS/text messages", "A type of mobile virus", "Spam emails on mobile"],
                "correct_option": "B",
                "explanation": "Smishing uses SMS text messages to lure victims into clicking malicious links or calling fraudulent numbers.",
                "difficulty": "easy"
            },
            {
                "category": "mobile_security",
                "text": "Why is keeping your mobile operating system updated critical?",
                "options": ["To get new emojis", "To patch known security vulnerabilities exploited by hackers", "To free up storage space", "To improve camera quality"],
                "correct_option": "B",
                "explanation": "OS updates primarily deliver security patches that fix zero-day exploits and known vulnerabilities.",
                "difficulty": "medium"
            },
            {
                "category": "mobile_security",
                "text": "What risk does an outdated 'Flashlight' app requesting access to your Contacts and Microphone pose?",
                "options": ["Overheating the phone", "Excessive battery drain", "Data harvesting and privacy violation", "Breaking the camera LED"],
                "correct_option": "C",
                "explanation": "Apps requesting permissions unrelated to their core function are often designed to harvest and sell user data.",
                "difficulty": "medium"
            },
            # Banking Fraud
            {
                "category": "banking_fraud",
                "text": "Your bank calls you asking for the OTP you just received to 'block a fraudulent transaction'. What do you do?",
                "options": ["Provide the OTP immediately to stop the fraud", "Hang up; banks never ask for OTPs over the phone", "Ask them to verify your account balance first", "Forward the SMS to the caller"],
                "correct_option": "B",
                "explanation": "Legitimate banks will never ask you to read out an OTP. The caller is the fraudster trying to authorize a transaction.",
                "difficulty": "easy"
            },
            {
                "category": "banking_fraud",
                "text": "What is a 'Card Skimmer'?",
                "options": ["A person who steals credit cards", "A malicious device attached to ATMs to steal magnetic stripe data and PINs", "Software that predicts credit card numbers", "A type of online payment gateway"],
                "correct_option": "B",
                "explanation": "Skimmers are physical devices overlaid on card readers to clone your card data.",
                "difficulty": "medium"
            },
            {
                "category": "banking_fraud",
                "text": "What is the safest way to log into your online banking portal?",
                "options": ["Clicking a link from an email", "Searching for the bank on Google and clicking the first ad", "Typing the exact URL directly into the browser address bar", "Using a link provided in a text message"],
                "correct_option": "C",
                "explanation": "Typing the URL ensures you don't accidentally click a phishing link or a spoofed search engine ad.",
                "difficulty": "easy"
            },
            {
                "category": "banking_fraud",
                "text": "What should you do if you notice a small, unauthorized $1 charge on your credit card?",
                "options": ["Ignore it since it's a small amount", "Wait a month to see if more charges appear", "Contact your bank immediately; fraudsters use small charges to test stolen cards", "Dispute it with the merchant directly"],
                "correct_option": "C",
                "explanation": "Fraudsters often perform a 'test transaction' for a tiny amount to verify the card is active before making large purchases.",
                "difficulty": "medium"
            },
            {
                "category": "banking_fraud",
                "text": "What is a 'Money Mule'?",
                "options": ["A secure armored vehicle", "Someone who transfers illegally acquired money on behalf of others, often unknowingly", "A type of banking trojan", "An offshore bank account"],
                "correct_option": "B",
                "explanation": "Fraudsters recruit money mules (often via fake job offers) to launder stolen funds, making the mule legally liable.",
                "difficulty": "hard"
            },
            # Privacy Protection
            {
                "category": "privacy_protection",
                "text": "What is the purpose of a VPN (Virtual Private Network)?",
                "options": ["To speed up your internet connection", "To encrypt your internet traffic and mask your IP address", "To block all advertisements", "To prevent hardware viruses"],
                "correct_option": "B",
                "explanation": "A VPN creates an encrypted tunnel for your traffic, protecting your data from ISP tracking and local network snooping.",
                "difficulty": "medium"
            },
            {
                "category": "privacy_protection",
                "text": "Why should you cover your webcam when not in use?",
                "options": ["To save battery", "To prevent dust accumulation", "To prevent malicious actors from spying on you using Remote Access Trojans (RATs)", "To improve video processing speed"],
                "correct_option": "C",
                "explanation": "Malware can secretly activate your webcam. A physical cover provides foolproof privacy.",
                "difficulty": "easy"
            },
            {
                "category": "privacy_protection",
                "text": "What is 'Doxxing'?",
                "options": ["Sending documents via email", "Publishing private or identifying information about a particular individual on the internet", "A type of data encryption", "Deleting someone's social media account"],
                "correct_option": "B",
                "explanation": "Doxxing is malicious exposure of personal details (address, phone number) to encourage harassment.",
                "difficulty": "medium"
            },
            {
                "category": "privacy_protection",
                "text": "Which browser mode prevents the browser from saving your history, cookies, and site data?",
                "options": ["Safe Mode", "Incognito / Private Browsing Mode", "Developer Mode", "Reader Mode"],
                "correct_option": "B",
                "explanation": "Incognito mode prevents local data storage but does not hide your activity from your ISP or the websites you visit.",
                "difficulty": "easy"
            },
            {
                "category": "privacy_protection",
                "text": "What does a privacy policy primarily detail?",
                "options": ["The cost of the software", "How a company collects, uses, shares, and protects your data", "The copyright terms of the application", "The rules for interacting with other users"],
                "correct_option": "B",
                "explanation": "Privacy policies outline the legal framework for how your personal information is handled by the service provider.",
                "difficulty": "medium"
            },
            # Public WiFi
            {
                "category": "public_wifi",
                "text": "What is the biggest risk of using unsecured Public WiFi?",
                "options": ["Slower internet speeds", "Data interception by attackers on the same network (Man-in-the-Middle attacks)", "Getting banned from the cafe", "Using too much bandwidth"],
                "correct_option": "B",
                "explanation": "Unsecured WiFi transmits data in cleartext, allowing attackers to intercept passwords and cookies.",
                "difficulty": "medium"
            },
            {
                "category": "public_wifi",
                "text": "If you MUST use Public WiFi, what tool is essential to protect your data?",
                "options": ["An Antivirus program", "A Virtual Private Network (VPN)", "A Password Manager", "Incognito mode"],
                "correct_option": "B",
                "explanation": "A VPN encrypts your traffic before it leaves your device, making it unreadable to anyone snooping on the network.",
                "difficulty": "easy"
            },
            {
                "category": "public_wifi",
                "text": "What is an 'Evil Twin' attack?",
                "options": ["Two hackers working together", "A rogue WiFi hotspot set up to mimic a legitimate public network", "A cloned hard drive", "A duplicated email account"],
                "correct_option": "B",
                "explanation": "Attackers create a network with the same name (e.g., 'Starbucks WiFi') to trick users into connecting to their malicious router.",
                "difficulty": "hard"
            },
            {
                "category": "public_wifi",
                "text": "Which activity should you completely avoid on Public WiFi?",
                "options": ["Reading the news", "Streaming music", "Logging into your bank account", "Checking the weather"],
                "correct_option": "C",
                "explanation": "Financial transactions and entering sensitive credentials should never be done on untrusted networks.",
                "difficulty": "easy"
            },
            {
                "category": "public_wifi",
                "text": "Why should you disable 'Auto-connect to WiFi networks' on your devices?",
                "options": ["To save battery life", "To prevent your device from silently connecting to malicious rogue hotspots", "To avoid data roaming charges", "To speed up the processor"],
                "correct_option": "B",
                "explanation": "If auto-connect is on, an attacker can broadcast a known SSID and your phone will connect to it without your knowledge.",
                "difficulty": "medium"
            },
            # UPI Scams
            {
                "category": "upi_scams",
                "text": "A buyer on an online marketplace says they sent a 'Request Money' link for you to receive payment. What should you do?",
                "options": ["Enter your UPI PIN to accept the money", "Decline it; you never enter a UPI PIN to receive money, only to send it", "Share your bank account details instead", "Call customer support to verify the link"],
                "correct_option": "B",
                "explanation": "Entering a UPI PIN authorizes a deduction from your account. You NEVER need a PIN to receive funds.",
                "difficulty": "easy"
            },
            {
                "category": "upi_scams",
                "text": "What is a common trick used in 'Screen Sharing' UPI scams?",
                "options": ["Sending a malicious PDF", "Asking you to download apps like AnyDesk or TeamViewer to 'help' with a refund", "Calling you on WhatsApp video", "Sending a fake QR code"],
                "correct_option": "B",
                "explanation": "Scammers use remote desktop apps to view your screen, read your OTPs, and initiate UPI transfers.",
                "difficulty": "medium"
            },
            {
                "category": "upi_scams",
                "text": "You scan a QR code at a local shop to pay. What is the most critical detail to check before entering your PIN?",
                "options": ["The color of the QR code", "The merchant's name displayed on the payment screen", "The speed of the internet connection", "The battery percentage of your phone"],
                "correct_option": "B",
                "explanation": "Fraudsters sometimes paste their own QR codes over legitimate ones. Always verify the receiver's name.",
                "difficulty": "easy"
            },
            {
                "category": "upi_scams",
                "text": "What happens if you approve a collect request from an unknown VPA (Virtual Payment Address)?",
                "options": ["You receive money", "Money is deducted from your linked bank account", "Your account gets blocked", "Nothing happens"],
                "correct_option": "B",
                "explanation": "A collect request is a demand for payment. Approving it and entering your PIN sends your money to the requester.",
                "difficulty": "medium"
            },
            {
                "category": "upi_scams",
                "text": "A fake customer care executive asks you to forward an SMS containing a complex code to verify your identity. What are they likely doing?",
                "options": ["Verifying your phone number", "Registering your mobile number on a new UPI app on their device", "Checking your network strength", "Activating international roaming"],
                "correct_option": "B",
                "explanation": "Forwarding device-binding SMS codes allows fraudsters to link your bank account to their UPI application.",
                "difficulty": "hard"
            },
            # Device Security
            {
                "category": "device_security",
                "text": "What is the purpose of Full Disk Encryption (like BitLocker or FileVault)?",
                "options": ["To compress files to save space", "To protect data from being read if the device is lost or stolen", "To prevent viruses from entering the computer", "To speed up hard drive performance"],
                "correct_option": "B",
                "explanation": "Encryption scrambles your data. Without the decryption key (your password), a thief cannot read the hard drive even if they remove it.",
                "difficulty": "medium"
            },
            {
                "category": "device_security",
                "text": "Why should you always lock your computer screen when stepping away from your desk?",
                "options": ["To save electricity", "To prevent 'shoulder surfing' and unauthorized physical access to your logged-in accounts", "To stop background updates", "To allow the screen saver to run"],
                "correct_option": "B",
                "explanation": "An unlocked computer grants an insider or passerby immediate access to your emails, files, and internal networks.",
                "difficulty": "easy"
            },
            {
                "category": "device_security",
                "text": "What is the danger of plugging a random USB drive you found into your computer?",
                "options": ["It might short-circuit the USB port", "It can automatically execute malicious payloads (like keystroke loggers or ransomware)", "It will delete your existing files", "It will format your hard drive instantly"],
                "correct_option": "B",
                "explanation": "Malicious USBs can act as keyboards to inject commands (Rubber Ducky) or exploit autorun features to install malware.",
                "difficulty": "medium"
            },
            {
                "category": "device_security",
                "text": "What is a 'Zero-Day' vulnerability?",
                "options": ["A virus that deletes data in zero days", "A software flaw unknown to the vendor, meaning no patch currently exists", "A computer that has never been turned on", "A network with zero security"],
                "correct_option": "B",
                "explanation": "It's called a 'Zero-Day' because the developers have had zero days to fix it before attackers started exploiting it.",
                "difficulty": "hard"
            },
            {
                "category": "device_security",
                "text": "Which feature helps locate, lock, or wipe a lost mobile device remotely?",
                "options": ["Airplane Mode", "Find My Device / Find My iPhone", "Bluetooth Sharing", "Battery Saver"],
                "correct_option": "B",
                "explanation": "These built-in MDM (Mobile Device Management) features allow you to secure your data even if the physical device is compromised.",
                "difficulty": "easy"
            },
            # Safe Browsing
            {
                "category": "safe_browsing",
                "text": "What does a browser warning stating 'Your connection is not private' indicate?",
                "options": ["Your ISP is tracking you", "The website's SSL/TLS certificate is invalid, expired, or mismatched", "The website is currently offline", "You are using a VPN"],
                "correct_option": "B",
                "explanation": "This warning means the encryption cannot be trusted, and you might be facing a Man-in-the-Middle attack.",
                "difficulty": "medium"
            },
            {
                "category": "safe_browsing",
                "text": "What are 'Cookies' in the context of web browsing?",
                "options": ["Small pieces of malware", "Small text files used to remember stateful information like login sessions and tracking preferences", "Browser extensions that block ads", "Temporary internet files used for caching images"],
                "correct_option": "B",
                "explanation": "Cookies maintain your session so you don't have to log in on every page, but third-party cookies track you across sites.",
                "difficulty": "easy"
            },
            {
                "category": "safe_browsing",
                "text": "Why is it dangerous to download cracked or pirated software?",
                "options": ["It is illegal", "It often comes bundled with trojans, ransomware, or cryptominers", "It runs slower than paid software", "It lacks customer support"],
                "correct_option": "B",
                "explanation": "While illegal, the primary security risk is that attackers modify pirated software to establish backdoors on your system.",
                "difficulty": "easy"
            },
            {
                "category": "safe_browsing",
                "text": "What is 'Typosquatting'?",
                "options": ["Typing a password incorrectly too many times", "Registering domain names similar to popular websites (e.g., faceb00k.com) to deceive users", "Using a broken keyboard", "Squatting on an IP address"],
                "correct_option": "B",
                "explanation": "Attackers rely on users making typographical errors to direct them to fake login pages or malware domains.",
                "difficulty": "medium"
            },
            {
                "category": "safe_browsing",
                "text": "What does an ad-blocker do besides hiding annoying advertisements?",
                "options": ["It speeds up your processor", "It prevents 'Malvertising' (malicious code hidden in ad networks) from executing in your browser", "It blocks all tracking cookies permanently", "It hides your IP address"],
                "correct_option": "B",
                "explanation": "Ad networks are frequently compromised. Ad-blockers prevent malicious scripts loaded from third-party ad servers from running.",
                "difficulty": "hard"
            }
        ]

        count = 0
        for q in questions_data:
            SecurityQuestion.objects.create(
                category=q['category'],
                text=q['text'],
                option_a=q['options'][0],
                option_b=q['options'][1],
                option_c=q['options'][2],
                option_d=q['options'][3],
                correct_option=q['correct_option'],
                explanation=q['explanation'],
                difficulty=q['difficulty']
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} security questions."))

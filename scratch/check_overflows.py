import os
import sys
import time
from playwright.sync_api import sync_playwright

PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"

BREAKPOINTS = [320, 375, 425, 768, 1024, 1280, 1440, 1920]

PAGES = {
    "home": "",
    "cyber_crimes": "cyber-crimes/",
    "crime_detail": "crime/228984db-5f08-4a77-b034-a0747a88609b/",
    "report_crime": "report/",
    "reporting_guide": "reporting-guide/",
    "risk_calculator": "risk-calculator/",
    "contact": "contact/",
    "citizen_safety": "citizen-safety/",
    "email_breach": "email-breach-check/",
    "phone_exposure": "phone-exposure-check/",
    "aadhaar_risk": "aadhaar-risk-check/",
    "financial_risk": "financial-risk-scan/",
    "kyc_shield": "kyc-document-shield/",
    "password_scan": "password-strength-scan/",
    "scorecard": "scorecard/",
    "assessment": "assessment/"
}

def run():
    print("Checking for horizontal overflows on public pages...")
    overflows_found = False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for name, path in PAGES.items():
            url = f"{BASE_URL}/{path}"
            print(f"Auditing page: {name} ({url})")
            
            for width in BREAKPOINTS:
                page.set_viewport_size({"width": width, "height": 800})
                
                try:
                    page.goto(url)
                    time.sleep(0.5) # Wait for page load and rendering
                    
                    # Evaluate horizontal scroll width vs inner width
                    scroll_width = page.evaluate("document.documentElement.scrollWidth")
                    inner_width = page.evaluate("window.innerWidth")
                    
                    # Check if body has horizontal scroll or overflow-x is active
                    has_overflow = scroll_width > inner_width
                    
                    if has_overflow:
                        print(f"  [OVERFLOW] Width {width}px: scrollWidth={scroll_width}px, innerWidth={inner_width}px")
                        overflows_found = True
                except Exception as e:
                    print(f"  Error loading {name} at {width}px: {e}")

        browser.close()
    
    if not overflows_found:
        print("Success: No horizontal overflows found on any public pages across all tested breakpoints!")
    else:
        print("Audit complete: Horizontal overflows detected on some pages/breakpoints.")

if __name__ == "__main__":
    run()

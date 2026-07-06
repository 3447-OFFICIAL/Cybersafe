import time
from playwright.sync_api import sync_playwright

PORT = 8000
URL = f"http://127.0.0.1:{PORT}/email-breach-check/"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Set mobile view
        page.set_viewport_size({"width": 320, "height": 800})
        page.goto(URL)
        time.sleep(1) # Let it render
        
        # Execute JS to find overflowing elements
        overflowing_elements = page.evaluate("""
            () => {
                const results = [];
                const innerWidth = window.innerWidth;
                const elems = document.querySelectorAll('*');
                for (const el of elems) {
                    if (el.closest('#navbarNav') || el.closest('#acc-premium-widget') || el.closest('.chatbot-toggle-wrapper') || el.closest('.acc-panel') || el.closest('.chatbot-widget')) {
                        continue;
                    }
                    const rect = el.getBoundingClientRect();
                    if (rect.right > innerWidth) {
                        results.push({
                            tagName: el.tagName,
                            id: el.id,
                            className: el.className,
                            right: rect.right,
                            width: rect.width,
                            parent: el.parentElement ? el.parentElement.tagName : 'none'
                        });
                    }
                }
                return results;
            }
        """)
        
        print(f"Found {len(overflowing_elements)} elements overflowing on mobile width (375px):")
        for i, el in enumerate(overflowing_elements[:15]):
            print(f"{i+1}. <{el['tagName']} id='{el['id']}' class='{el['className']}'> inside <{el['parent']}>: right={el['right']}px, width={el['width']}px")
            
        browser.close()

if __name__ == "__main__":
    run()

from playwright.sync_api import Page, expect, sync_playwright

def test_streamlit_app(page: Page):
    try:
        page.goto("http://localhost:8501", timeout=60000)
        # Wait for load - Streamlit can be slow
        page.wait_for_load_state("networkidle")

        # Take screenshot for debug
        page.screenshot(path="/home/jules/verification/debug.png")

        # Check text - use looser matching
        # st.title("🤖 Intent Extraction Agent")
        expect(page.get_by_role("heading", name="Intent Extraction Agent")).to_be_visible()

        expect(page.get_by_text("Thought Process")).to_be_visible()
        expect(page.get_by_placeholder("What would you like to build?")).to_be_visible()

        page.screenshot(path="/home/jules/verification/verification.png")
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")
        page.screenshot(path="/home/jules/verification/error.png")
        # Print body text to see what's there
        print(page.inner_text("body"))

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_streamlit_app(page)
        finally:
            browser.close()

from playwright.sync_api import sync_playwright
from langchain_core.tools import tool


@tool
def browse_page(url: str) -> str:
    """Open a webpage and extract its visible text content."""

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            title = page.title()
            content = page.locator("body").inner_text()

            browser.close()

            return f"Page title: {title}\n\nContent:\n{content[:10000]}"

    except Exception as e:
        return f"Browser error: {str(e)}"


browser_tools = [browse_page]


from playwright.async_api import async_playwright
from langchain_core.tools import tool


MAX_PAGE_CHARS = 3000


@tool
async def browse_page(url: str) -> str:
    """
    Open a webpage using Chromium and return limited visible text.
    """

    try:

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True
            )

            try:

                page = await browser.new_page()

                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=20000
                )

                title = await page.title()

                content = await page.locator("body").inner_text(
                    timeout=10000
                )

                content = content[:MAX_PAGE_CHARS]

                return (
                    f"Page title: {title}\n\n"
                    f"Content:\n{content}\n\n"
                    "[Content truncated if necessary.]"
                )

            finally:
                await browser.close()

    except Exception as exc:

        return f"BROWSER_ERROR: {str(exc)}"


browser_tools = [browse_page]

import asyncio
import os
from playwright.async_api import async_playwright
import json
from plugins.web.process_html import process_html_content


script_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = "data/cookies"

folder_name = os.path.join(script_dir, folder_name)
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

COOKIES_FILE = os.path.join(folder_name, "cookies.json")


async def save_cookies(context):
    cookies = await context.cookies()
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)


async def load_cookies(context):
    try:
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
    except FileNotFoundError:
        return
    await context.add_cookies(cookies)


async def get_content_with_playwright_async(url, headless=False):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        context = await browser.new_context(
            storage_state={"cookies": [], "origins": []}, user_agent=user_agent
        )
        context.set_default_timeout(30000)
        page = await context.new_page()

        try:
            # Load stored cookies if available
            await load_cookies(context)

            await page.goto(url, wait_until="networkidle")
            # Save the cookies
            await save_cookies(context)
            html = await page.content()
            return html if html else ""
        except Exception as e:
            print(e)
            await browser.close()
            return None
        finally:
            await browser.close()


async def get_text_with_playwright(url, headless=False, extract_tags=None):
    html = await get_content_with_playwright_async(url, headless=headless)

    content = process_html_content(html, extract_tags=extract_tags)

    return content if content else ""


async def get_content_for_urls(urls: list):
    """
    all_content_tasks = [get_content_with_playwright(url) for url in urls]

    all_content = await asyncio.gather(*all_content_tasks)

    urls_and_content = [*zip(urls, all_content)]


    return urls_and_content
    """
    all_content_tasks = [get_content_with_playwright_async(url) for url in urls]
    all_content = await asyncio.gather(*all_content_tasks)
    urls_and_content = [*zip(urls, all_content)]
    return urls_and_content

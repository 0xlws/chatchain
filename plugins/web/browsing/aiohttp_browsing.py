import aiohttp
import asyncio

from plugins.web.process_html import process_html_content


async def get_content_with_aiohttp(url, extract_tags=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()

    return html if html else ""


async def get_text_with_aiohttp(url, extract_tags=None, ddg=False):
    html = await get_content_with_aiohttp(url, extract_tags=extract_tags)
    content = process_html_content(html, extract_tags=extract_tags, ddg=ddg)
    return content if content else ""


async def main():
    url = "https://example.com/"
    extract_tags = "p"  # Use None if you want all the tags
    # extract_tags = None

    content = await get_content_with_aiohttp(url, extract_tags)

    if extract_tags:
        for i, paragraph in enumerate(content, start=1):
            print(f"{i}. {paragraph}")
    else:
        print("Inner text:", content)
        print("Length of text content:", len(content))


if __name__ == "__main__":
    asyncio.run(main())

from ..browsing.playwright_browsing import get_content_with_playwright_async
from ..browsing.aiohttp_browsing import get_content_with_aiohttp
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def parse_search_results(html_content, max_results, exclude_ads, allow_same_base_urls):
    soup = BeautifulSoup(html_content, "html.parser")

    search_results = []
    base_urls = set()
    try:
        for result in soup.find_all("div", class_="result__body"):
            if exclude_ads and result.parent.get("class", "").count("result--ad"):
                continue
            url = result.find("a", class_="result__url")["href"]
            if ".pdf" in url:
                continue
            base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
            title = clean_text(result.find("a", class_="result__url").text)
            snippet = clean_text(result.find("a", class_="result__snippet").text)

            if not allow_same_base_urls:
                search_results.append((title, url, snippet))
            elif allow_same_base_urls or base_url not in base_urls:
                search_results.append((title, url, snippet))
                base_urls.add(base_url)
            if len(search_results) >= max_results:
                break
    except Exception as e:
        print(e)

    return search_results


async def ddg_search(query, max_results=20):
    url = f"https://duckduckgo.com/html/?q={query}&df=m"
    html_content = await get_content_with_aiohttp(url)
    search_results = parse_search_results(html_content, max_results, True, True)

    if not search_results:
        html_content = await get_content_with_playwright_async(url, headless=True)
        search_results = parse_search_results(html_content, max_results, True, True)

    formatted_results = []
    for index, (title, url, snippet) in enumerate(search_results, start=1):
        formatted_result = {
            "index": index,
            "title": title,
            "url": url,
            "snippet": snippet,
        }
        formatted_results.append(formatted_result)
        print(f"Result {index}:\nTitle: {title}\nURL: {url}\nSnippet: {snippet}\n")

    return formatted_results


if __name__ == "__main__":
    pass

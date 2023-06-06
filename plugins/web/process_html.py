from bs4 import BeautifulSoup


def process_html_content(html, extract_tags=None, text=False, ddg=False):
    soup = BeautifulSoup(html, "html.parser")

    # Remove script tags
    for script in soup("script"):
        script.decompose()

    if text:
        if extract_tags:
            content = " ".join(
                [tag.get_text(strip=True) for tag in soup.find_all(extract_tags)]
            )
        else:
            content = " ".join(soup.stripped_strings).replace("\n\n", " ")

        return content
    return soup


def split_html_by_tags(html, extract_tags=None, text=False, ddg=False):
    soup = BeautifulSoup(html, "html.parser")

    # Remove script tags
    for script in soup("script"):
        script.decompose()

    return [str(tag) for tag in soup.find_all()]

import requests
from bs4 import BeautifulSoup


def scrape_article(url):
    """
    Scrapes the text content of a news article.

    Parameters
    ----------
    url : str
        URL of the news article

    Returns
    -------
    str
        Extracted article text
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted elements
        for tag in soup([
            "script",
            "style",
            "noscript",
            "header",
            "footer",
            "nav",
            "aside",
            "form",
            "svg"
        ]):
            tag.decompose()

        paragraphs = soup.find_all("p")

        article = []

        for p in paragraphs:

            text = p.get_text(" ", strip=True)

            if len(text) > 40:
                article.append(text)

        article_text = " ".join(article)

        if len(article_text) < 200:
            return "Preview unavailable for this article."

        return article_text

    except Exception:

        return "Unable to retrieve article preview."

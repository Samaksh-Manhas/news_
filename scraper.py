import requests
from bs4 import BeautifulSoup


def scrape_article(url):
    """
    Scrapes the main text from a news article.

    Parameters
    ----------
    url : str
        Article URL

    Returns
    -------
    str
        Clean article text
    """

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted tags
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

            text = p.get_text(strip=True)

            if len(text) > 40:
                article.append(text)

        article = " ".join(article)

        return article

    except Exception as e:

        print("Scraping Error:", e)

        return ""

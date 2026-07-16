from newsapi import NewsApiClient

NEWS_API_KEY = "88fca811c1494f87a97b0d78426e16a9"

newsapi = NewsApiClient(api_key=NEWS_API_KEY)


def search_news(query, page_size=5):
    """
    Search NewsAPI for articles related to the user's headline.

    Parameters
    ----------
    query : str
        User entered headline.

    page_size : int
        Number of articles to return.

    Returns
    -------
    list
        List of article dictionaries.
    """

    try:

        response = newsapi.get_everything(

            q=query,

            language="en",

            sort_by="relevancy",

            search_in="title,description,content",

            page_size=page_size

        )

        if response["status"] != "ok":

            return None

        articles = []

        for article in response["articles"]:

            title = article.get("title") or ""

            description = article.get("description") or ""

            content = article.get("content") or ""

            source = article.get("source", {}).get("name", "Unknown")

            author = article.get("author") or "Unknown"

            published = article.get("publishedAt") or "Unknown"

            url = article.get("url") or ""

            image = article.get("urlToImage")

            news = f"{title} {description}"

            articles.append({

                "title": title,

                "description": description,

                "content": content,

                "news": news,

                "source": source,

                "author": author,

                "published": published,

                "url": url,

                "image": image

            })

        return articles

    except Exception as e:

        print("NewsAPI Error:", e)

        return None

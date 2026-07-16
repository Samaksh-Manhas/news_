from newsapi import NewsApiClient

NEWS_API_KEY = "b21c695c2f3e4a6baa4df1f2869413be"

newsapi = NewsApiClient(api_key=NEWS_API_KEY)


def search_news(query, page_size=5):
    """
    Searches NewsAPI for articles related to the given headline.

    Parameters
    ----------
    query : str
        News headline entered by the user.

    page_size : int
        Number of articles to fetch.

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

            page_size=page_size

        )

        if response["status"] != "ok":

            return []

        articles = []

        for article in response["articles"]:

            articles.append({

                "title": article["title"],

                "description": article["description"],

                "content": article["content"],

                "source": article["source"]["name"],

                "author": article["author"],

                "published": article["publishedAt"],

                "url": article["url"],

                "image": article["urlToImage"]

            })

        return articles

    except Exception as e:

        print("NewsAPI Error:", e)

        return []

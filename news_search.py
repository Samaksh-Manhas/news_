from newsapi import NewsApiClient

NEWS_API_KEY = "b21c695c2f3e4a6baa4df1f2869413be"

newsapi = NewsApiClient(api_key=NEWS_API_KEY)


def search_news(headline):

    articles = newsapi.get_everything(
        q=headline,
        language="en",
        sort_by="relevancy",
        page_size=5
    )

    return articles["articles"]
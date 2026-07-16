import streamlit as st
import joblib
import re
import string

from news_search import search_news
from scraper import scrape_article

from sklearn.metrics.pairwise import cosine_similarity

# --------------------------
# Load Model
# --------------------------

model = joblib.load("fake_news_model.pkl")
tfidf = joblib.load("tfidf_vectorizer.pkl")

# --------------------------
# Cleaning Function
# --------------------------

def clean_text(text):

    text = text.lower()

    text = re.sub(r"http\S+|www\S+", "", text)

    text = re.sub(r"<.*?>", "", text)

    text = text.translate(
        str.maketrans("", "", string.punctuation)
    )

    text = re.sub(r"\d+", "", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text

# --------------------------
# Streamlit UI
# --------------------------

st.set_page_config(
    page_title="Fake News Verifier",
    page_icon="📰",
    layout="wide"
)

st.title("Fake News & Misinformation Verifier")

st.write(
    "Enter a news headline to search trusted sources and classify the retrieved articles."
)

headline = st.text_input(
    "Enter News Headline"
)

if st.button("Verify News"):

    if headline.strip() == "":
        st.warning("Please enter a headline.")
        st.stop()

    articles = search_news(headline)

    if len(articles) == 0:
        st.error("No matching articles found.")
        st.stop()

    headline_vector = tfidf.transform(
        [clean_text(headline)]
    )

    for article in articles:

        st.divider()

        st.subheader(article["title"])

        st.write("**Source:**", article["source"]["name"])

        st.write(article["url"])

        article_text = scrape_article(
            article["url"]
        )

        article_clean = clean_text(article_text)

        vector = tfidf.transform([article_clean])

        prediction = model.predict(vector)[0]

        probability = model.predict_proba(vector)[0]

        article_vector = tfidf.transform(
            [clean_text(article["title"])]
        )

        similarity = cosine_similarity(
            headline_vector,
            article_vector
        )[0][0]

        confidence = max(probability) * 100

        if prediction == 1:
            st.success(
                f"Prediction: REAL ({confidence:.2f}%)"
            )
        else:
            st.error(
                f"Prediction: FAKE ({confidence:.2f}%)"
            )

        st.progress(float(confidence/100))

        st.write(
            f"Headline Similarity: {similarity*100:.2f}%"
        )

        with st.expander("Article Preview"):

            st.write(article_text[:1500])
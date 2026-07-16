import streamlit as st
import joblib
import re
import string

from sklearn.metrics.pairwise import cosine_similarity

from news_search import search_news
from scraper import scrape_article

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Fake News Verification System",
    page_icon="📰",
    layout="wide"
)

# ==========================================
# LOAD MODEL
# ==========================================

model = joblib.load("fake_news_model.pkl")
tfidf = joblib.load("tfidf_vectorizer.pkl")

# ==========================================
# TEXT CLEANING
# ==========================================

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

# ==========================================
# HEADER
# ==========================================

st.title("AI Fake News Verification System")

st.write(
"""
This application predicts whether a news headline is **Likely Real**
or **Likely Fake** using a Machine Learning model.

It also searches recent news articles from trusted sources
to provide supporting evidence.
"""
)

st.divider()

headline = st.text_input(
    "Enter a News Headline"
)

verify = st.button("Verify News")

# ==========================================
# START
# ==========================================

if verify:

    if headline.strip() == "":

        st.warning("Please enter a news headline.")

        st.stop()

    clean_headline = clean_text(headline)

    vector = tfidf.transform([clean_headline])

    prediction = model.predict(vector)[0]

    probability = model.predict_proba(vector)[0]

    fake_probability = probability[0] * 100

    real_probability = probability[1] * 100

    # ==========================================
    # PREDICTION
    # ==========================================

    st.divider()

    st.subheader("Overall Prediction")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Real Probability",
            f"{real_probability:.2f}%"
        )

        st.progress(real_probability / 100)

    with col2:

        st.metric(
            "Fake Probability",
            f"{fake_probability:.2f}%"
        )

        st.progress(fake_probability / 100)

    st.divider()

    if prediction == 1:

        st.success(
            f"""
            **Likely REAL News**

            Confidence: **{real_probability:.2f}%**
            """
        )

    else:

        st.error(
            f"""
            **Likely FAKE News**

            Confidence: **{fake_probability:.2f}%**
            """
        )

    st.divider()

    # ==========================================
    # SEARCH SUPPORTING ARTICLES
    # ==========================================

    st.subheader("Supporting News Articles")

    with st.spinner("Searching latest news..."):

        articles = search_news(clean_headline)

    if articles is None:

        st.error(
            """
            **NewsAPI Error**

            Unable to fetch live news. Please check your API key or rate limits.
            """
        )
        
        st.stop()

    elif len(articles) == 0:

        st.warning(
            """
            No supporting news articles were found.

            This DOES NOT necessarily mean
            the news is fake.

            It only means no matching articles
            were returned from NewsAPI.
            """
        )

    else:

        st.success(
            f"{len(articles)} Supporting Articles Found"
        )

        headline_vector = tfidf.transform(
            [clean_headline]
        )

        st.divider()

        st.subheader("Evidence")

        for article in articles:

            similarity = cosine_similarity(

                headline_vector,

                tfidf.transform(
                    [clean_text(article["news"])]
                )

            )[0][0]

            similarity = similarity * 100

            with st.expander(f"📰 {article['title']} - Match: {similarity:.1f}%"):
                article_text = scrape_article(article["url"])
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Source:** {article['source']}")
                    st.write(f"**Published:** {article['published']}")
                
                with col2:
                    if similarity >= 80:
                        st.success(f"High Match\n\n{similarity:.2f}%")
                    elif similarity >= 50:
                        st.warning(f"Medium Match\n\n{similarity:.2f}%")
                    else:
                        st.error(f"Low Match\n\n{similarity:.2f}%")
                
                st.markdown(f"**🔗 Article Link:** {article['url']}")
                
                if article["description"]:
                    st.write(f"**Description:** {article['description']}")
                
                if len(article_text) > 100:
                    st.write(f"**Preview:** {article_text[:1500]}...")
                else:
                    st.info("Couldn't scrape the complete article text.")

        # ==========================================
        # FINAL VERDICT
        # ==========================================

        st.divider()

        st.subheader("Final Assessment")

        highest_similarity = max(
            [
                cosine_similarity(
                    headline_vector,
                    tfidf.transform(
                        [clean_text(article["news"])]
                    )
                )[0][0] * 100
                for article in articles
            ]
        )

        best_article = max(
            articles,
            key=lambda article: cosine_similarity(
                headline_vector,
                tfidf.transform(
                    [clean_text(article["news"])]
                )
            )[0][0]
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Supporting Articles",
                len(articles)
            )

        with col2:

            st.metric(
                "Highest Match",
                f"{highest_similarity:.2f}%"
            )

        with col3:

            if prediction == 1:

                st.metric(
                    "Model Prediction",
                    "Likely REAL"
                )

            else:

                st.metric(
                    "Model Prediction",
                    "Likely FAKE"
                )

        st.divider()

        if (prediction == 1 and highest_similarity >= 50) or highest_similarity >= 65:

            st.success(
                f"""
### ✅ Overall Verdict

The entered headline appears **Likely REAL**.

{ "Strong supporting evidence was found from trusted news sources, overriding the initial prediction." if (prediction == 0 and highest_similarity >= 65) else "The machine learning model predicts it is genuine, and we found supporting articles from trusted sources." }

**Best Matching Source:** {best_article['source']}
"""
            )

        elif prediction == 0 and highest_similarity < 65:

            st.error(
                """
### ❌ Overall Verdict

The entered headline appears **Likely FAKE**.

The machine learning model classified it as fake,
and no strong supporting evidence was found from
trusted news sources.
"""
            )

        else:

            st.warning(
                """
### ⚠️ Overall Verdict

The prediction is uncertain.

The machine learning model predicts this is real news,
but we could not find strong supporting evidence from
trusted news sources to verify it.

Please verify the news manually.
"""
            )

st.divider()

st.caption(
    "Developed using Python, Scikit-Learn, TF-IDF, Logistic Regression, BeautifulSoup, NewsAPI and Streamlit."
)

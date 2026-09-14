import streamlit as st

from sources import fetch_articles
from ai import analyze_article


st.set_page_config(
    page_title="eOppimisRadar",
    page_icon="📡",
    layout="wide"
)

st.title("eOppimisRadar")
st.subheader("AI Newsletter Assistant")

st.write(
    "Gather and analyze education, technology and learning-related information."
)


if st.button("Gather information"):

    with st.spinner("Fetching RSS articles..."):
        articles = fetch_articles(20)

    st.success(f"Found {len(articles)} articles.")

    results = []

    progress_bar = st.progress(0)

    status_text = st.empty()

    for index, article in enumerate(articles):

        status_text.write(
            f"Analyzing {index + 1}/{len(articles)}: "
            f"{article['title']}"
        )

        result = analyze_article(article)

        results.append(result)

        progress_bar.progress(
            (index + 1) / len(articles)
        )

    st.session_state["results"] = results

    status_text.empty()

    st.success("Analysis complete!")


if "results" in st.session_state:

    results = st.session_state["results"]

    relevant = [
        article
        for article in results
        if article["relevance"] >= 4
    ]

    review = [
        article
        for article in results
        if article["relevance"] == 3
    ]

    ignored = [
        article
        for article in results
        if article["relevance"] <= 2
    ]


    st.divider()

    st.header("Analysis results")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Relevant",
        len(relevant)
    )

    col2.metric(
        "Review",
        len(review)
    )

    col3.metric(
        "Ignored",
        len(ignored)
    )


    st.header("Relevant articles")

    if not relevant:
        st.info("No relevant articles found.")

    for article in relevant:

        with st.expander(
            f"✅ {article['source']} — {article['title']}"
        ):

            st.write(
                f"**Relevance:** {article['relevance']}/5"
            )

            st.write(
                f"**Summary:** {article['summary']}"
            )

            st.write(
                f"**Reason:** {article['reason']}"
            )

            if article["topics"]:

                st.write(
                    "**Topics:** "
                    + ", ".join(article["topics"])
                )

            if article["link"]:

                st.link_button(
                    "Open source",
                    article["link"]
                )


    st.header("Articles for review")

    if not review:
        st.info("No articles require review.")

    for article in review:

        with st.expander(
            f"🟡 {article['source']} — {article['title']}"
        ):

            st.write(
                f"**Relevance:** {article['relevance']}/5"
            )

            st.write(
                f"**Summary:** {article['summary']}"
            )

            st.write(
                f"**Reason:** {article['reason']}"
            )

            if article["topics"]:

                st.write(
                    "**Topics:** "
                    + ", ".join(article["topics"])
                )

            if article["link"]:

                st.link_button(
                    "Open source",
                    article["link"]
                )


    with st.expander(
        f"❌ Ignored articles ({len(ignored)})"
    ):

        for article in ignored:

            st.write(
                f"**{article['source']} — "
                f"{article['title']}**"
            )

            st.write(
                f"Relevance: {article['relevance']}/5"
            )

            st.write(article["reason"])

            st.divider()
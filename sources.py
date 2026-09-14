import feedparser


rss_sources = [
    {
        "name": "Google AI",
        "url": "https://blog.google/technology/ai/rss/"
    },
    {
        "name": "eSchool News",
        "url": "https://www.eschoolnews.com/feed/"
    },
    {
        "name": "Opetushallitus",
        "url": "https://oph.fi/fi/latest.rss"
    },
    {
        "name": "Theseus",
        "url": "https://www.theseus.fi/feed/rss_2.0/site"
    }
]


def fetch_articles(number_of_articles=20):
    """
    Fetch articles from all configured RSS feeds.

    Returns a list of dictionaries.
    Each dictionary contains:
    - source
    - title
    - link
    - description
    """

    articles = []

    for source in rss_sources:
        print(f"\nReading source: {source['name']}")

        feed = feedparser.parse(source["url"])

        if feed.bozo:
            print(
                f"Feed warning for {source['name']}: "
                f"{feed.bozo_exception}"
            )

        print(
            f"Entries available: {len(feed.entries)}"
        )

        entries = feed.entries[:number_of_articles]

        for entry in entries:
            title = entry.get(
                "title",
                "No title"
            )

            link = entry.get(
                "link",
                ""
            )

            description = entry.get(
                "summary",
                ""
            )

            if not description:
                description = entry.get(
                    "description",
                    ""
                )

            article = {
                "source": source["name"],
                "title": title,
                "link": link,
                "description": description
            }

            articles.append(article)

    return articles


if __name__ == "__main__":
    test_articles = fetch_articles(5)

    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)

    print(
        f"Total articles found: {len(test_articles)}"
    )

    for article in test_articles:
        print("\nSource:", article["source"])
        print("Title:", article["title"])
        print("Link:", article["link"])
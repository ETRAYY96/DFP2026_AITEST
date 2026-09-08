import feedparser
import requests
import json


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

feed_url = "https://www.theseus.fi/feed/rss_2.0/site"

model_name = "qwen2.5:7b"

number_of_articles = 10


# --------------------------------------------------
# READ RSS FEED
# --------------------------------------------------

feed = feedparser.parse(feed_url)

print("Feed:", feed.feed.get("title", "Unknown feed"))
print("Entries available in feed:", len(feed.entries))

# Take up to 10 articles
articles_to_check = feed.entries[:number_of_articles]

print("Articles to analyze:", len(articles_to_check))


# Lists for results
kept_articles = []
review_articles = []
ignored_articles = []


# --------------------------------------------------
# ANALYZE ARTICLES
# --------------------------------------------------

for index, article in enumerate(articles_to_check, start=1):

    title = article.get("title", "")
    link = article.get("link", "")
    summary = article.get("summary", "")

    print("\n" + "=" * 70)
    print(f"ARTICLE {index}")
    print("Title:", title)
    print("Link:", link)

    prompt = f"""
You are an information filtering assistant for Suomen eOppimiskeskus ry.

Your job is to decide whether a publication is genuinely relevant
to the organization's work.

Relevant topics include:

- digital learning
- online learning
- artificial intelligence in education
- educational technology
- digital competence
- accessibility in digital learning
- continuous learning
- future skills
- competence development
- changes in working life that affect learning or competence development
- research related to education, learning, digitalization or competence development

IMPORTANT RULES:

- Be strict.
- Do not invent connections that are not clearly present in the article.
- Only use information contained in the provided title and text.
- If the article is unrelated to education, learning, digital skills,
  educational technology, competence development or working-life learning,
  give it a low score.
- Do not recommend an article just because a weak indirect connection
  could be imagined.

Relevance scale:

1 = Not relevant

2 = Slightly related, but probably not useful

3 = Some relevance and should be reviewed by a human

4 = Clearly relevant to Suomen eOppimiskeskus ry

5 = Highly relevant and directly connected to the organization's work


ARTICLE TITLE:

{title}


ARTICLE TEXT:

{summary}


Return ONLY valid JSON in exactly this structure:

{{
    "summary_fi": "Short Finnish summary",
    "relevance": 1,
    "reason_fi": "Short explanation in Finnish",
    "topics": ["topic1", "topic2"],
    "newsletter_recommendation": false
}}


NEWSLETTER RULES:

- newsletter_recommendation = true only when relevance is 4 or 5
- newsletter_recommendation = false when relevance is 1, 2 or 3

Do not output anything outside the JSON.
"""

    try:

        # --------------------------------------------------
        # SEND ARTICLE TO OLLAMA
        # --------------------------------------------------

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0
                }
            },
            timeout=120
        )

        response.raise_for_status()

        raw_output = response.json()["response"]

        # Convert AI response into Python dictionary
        analysis = json.loads(raw_output)


        # --------------------------------------------------
        # PRINT AI ANALYSIS
        # --------------------------------------------------

        print("\nAI analysis:")

        print("Summary:", analysis["summary_fi"])

        print("Relevance:", analysis["relevance"])

        print("Reason:", analysis["reason_fi"])

        print("Topics:", analysis["topics"])

        print(
            "Newsletter:",
            analysis["newsletter_recommendation"]
        )


        # --------------------------------------------------
        # FILTER BASED ON RELEVANCE
        # --------------------------------------------------

        if analysis["relevance"] >= 4:

            print("\n✅ RELEVANT - KEEP ARTICLE")

            kept_articles.append({
                "title": title,
                "link": link,
                "summary": analysis["summary_fi"],
                "relevance": analysis["relevance"],
                "reason": analysis["reason_fi"],
                "topics": analysis["topics"]
            })


        elif analysis["relevance"] == 3:

            print("\n🟡 MAYBE - REVIEW ARTICLE")

            review_articles.append({
                "title": title,
                "link": link,
                "summary": analysis["summary_fi"],
                "relevance": analysis["relevance"],
                "reason": analysis["reason_fi"],
                "topics": analysis["topics"]
            })


        else:

            print("\n❌ IGNORE ARTICLE")

            ignored_articles.append({
                "title": title,
                "link": link,
                "relevance": analysis["relevance"]
            })


    except requests.exceptions.RequestException as error:

        print("\n⚠️ Error connecting to Ollama:")
        print(error)


    except json.JSONDecodeError as error:

        print("\n⚠️ AI returned invalid JSON:")
        print(error)
        print("Raw output:")
        print(raw_output)


    except Exception as error:

        print("\n⚠️ Error analyzing article:")
        print(error)


# --------------------------------------------------
# FINAL RESULTS
# --------------------------------------------------

print("\n")
print("=" * 70)
print("FINAL RESULTS")
print("=" * 70)

print("\nChecked articles:", len(articles_to_check))

print("✅ Relevant articles:", len(kept_articles))

print("🟡 Articles for review:", len(review_articles))

print("❌ Ignored articles:", len(ignored_articles))


# --------------------------------------------------
# SHOW RELEVANT ARTICLES
# --------------------------------------------------

if kept_articles:

    print("\n")
    print("=" * 70)
    print("RELEVANT ARTICLES")
    print("=" * 70)

    for article in kept_articles:

        print("\n✅", article["title"])
        print("Relevance:", article["relevance"])
        print("Summary:", article["summary"])
        print("Reason:", article["reason"])
        print("Topics:", article["topics"])
        print("Link:", article["link"])


# --------------------------------------------------
# SHOW ARTICLES THAT NEED HUMAN REVIEW
# --------------------------------------------------

if review_articles:

    print("\n")
    print("=" * 70)
    print("ARTICLES TO REVIEW")
    print("=" * 70)

    for article in review_articles:

        print("\n🟡", article["title"])
        print("Relevance:", article["relevance"])
        print("Summary:", article["summary"])
        print("Reason:", article["reason"])
        print("Topics:", article["topics"])
        print("Link:", article["link"])


print("\nAnalysis finished.")
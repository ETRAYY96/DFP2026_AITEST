import feedparser
import requests
import json

# RSS feed
feed_url = "https://yle.fi/rss/uutiset/paauutiset"

# Read RSS feed
feed = feedparser.parse(feed_url)

# Take the newest article
article = feed.entries[0]

title = article.title
link = article.link
summary = getattr(article, "summary", "")

# Prompt for the AI
prompt = f"""
You are an information filtering assistant for Suomen eOppimiskeskus ry.

Your job is to decide whether a publication is genuinely relevant to the organization's work.

Relevant topics include:
- digital learning
- online learning
- artificial intelligence in education
- educational technology
- digital competence
- accessibility in digital learning
- continuous learning
- future skills
- changes in working life that affect learning or competence development
- research related to education, learning, digitalization or competence development

IMPORTANT RULES:
- Be strict.
- Do not invent connections that are not clearly present in the article.
- If the article is unrelated to education, learning, digital skills, technology in learning, competence development or working-life learning, it should receive a low relevance score.
- Do not recommend an article just because a weak indirect connection could be imagined.
- Only use information contained in the provided title and text.

Relevance scale:
1 = Not relevant
2 = Slightly related, but not useful
3 = Some relevance, may be worth reviewing
4 = Clearly relevant
5 = Highly relevant and directly connected to the organization's work

ARTICLE TITLE:
{title}

ARTICLE TEXT:
{summary}

Return ONLY valid JSON in this exact format:

{{
  "summary_fi": "Short Finnish summary",
  "relevance": 1,
  "reason_fi": "Short explanation in Finnish",
  "topics": ["topic1", "topic2"],
  "newsletter_recommendation": false
}}

Rules for newsletter_recommendation:
- true only when relevance is 4 or 5
- false when relevance is 1, 2 or 3

Do not output anything outside the JSON.
"""

# Send article to Ollama
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
)

# Get AI output
raw_output = response.json()["response"]

print("\nOriginal article:")
print("Title:", title)
print("Link:", link)

# Convert AI output from JSON text into Python data
try:
    analysis = json.loads(raw_output)

    print("\nAI analysis:")
    print("Summary:", analysis["summary_fi"])
    print("Relevance:", analysis["relevance"])
    print("Reason:", analysis["reason_fi"])
    print("Topics:", analysis["topics"])
    print("Newsletter:", analysis["newsletter_recommendation"])

    # Filter article based on relevance
    if analysis["relevance"] >= 4:
        print("\n✅ KEEP ARTICLE")
    else:
        print("\n❌ IGNORE ARTICLE")

except json.JSONDecodeError:
    print("\nAI returned invalid JSON:")
    print(raw_output)
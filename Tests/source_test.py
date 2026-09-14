import feedparser
import requests
import json


# --------------------------------------------------
# RSS SOURCES
# --------------------------------------------------

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


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

model_name = "qwen2.5:7b"

# Maximum articles checked from EACH source
number_of_articles = 20


# --------------------------------------------------
# RESULT LISTS
# --------------------------------------------------

kept_articles = []
review_articles = []
ignored_articles = []


# --------------------------------------------------
# AI ANALYSIS FUNCTION
# --------------------------------------------------

def analyze_article(source_name, title, description, link):

    prompt = f"""
You are an information monitoring assistant for Suomen eOppimiskeskus ry.

Your task is to decide whether an article could be useful for the
organization, its members, or its member newsletter.

IMPORTANT:

The article does NOT need to mention Suomen eOppimiskeskus ry directly.

An article can be relevant if it discusses developments, research,
technology, policy, tools, projects, events or trends that could be
interesting to professionals working with education, learning,
digitalization or competence development.

The organization is interested in a BROAD range of topics.


RELEVANT TOPICS INCLUDE:

EDUCATION AND LEARNING
- teaching
- pedagogy
- learning
- studying
- schools
- universities
- universities of applied sciences
- vocational education
- higher education
- adult education
- lifelong learning
- continuous learning
- teacher education
- teacher professional development
- curriculum development
- assessment
- student learning
- learning research


DIGITAL LEARNING
- digital learning
- online learning
- e-learning
- remote learning
- hybrid learning
- blended learning
- digital learning environments
- learning management systems
- LMS platforms
- virtual classrooms
- digital learning materials
- digital teaching methods


ARTIFICIAL INTELLIGENCE
- artificial intelligence
- generative AI
- AI assistants
- AI agents
- AI tools
- AI in schools
- AI in universities
- AI in teaching
- AI in learning
- AI literacy
- responsible AI
- ethical AI
- AI regulation
- AI policy
- AI-supported learning
- AI-supported teaching


EDUCATIONAL TECHNOLOGY
- educational technology
- EdTech
- learning technology
- digital tools for teachers
- digital tools for students
- classroom technology
- emerging technologies
- virtual reality
- augmented reality
- immersive learning
- learning analytics
- adaptive learning
- personalized learning


DIGITAL SKILLS AND COMPETENCE
- digital competence
- digital literacy
- media literacy
- information literacy
- future skills
- technology skills
- competence development
- workforce skills
- reskilling
- upskilling


WORKING LIFE
- future of work
- changes in working life
- remote work
- hybrid work
- workplace learning
- digital transformation
- AI in working life
- automation
- professional development
- workforce competence


ACCESSIBILITY AND RESPONSIBILITY
- accessibility
- inclusive education
- digital accessibility
- equality in education
- responsible technology
- ethical technology
- data protection
- cybersecurity in education
- privacy
- sustainable technology
- sustainability


POLICY AND DEVELOPMENT
- education policy
- digital education policy
- AI policy
- education reform
- national education development
- European education initiatives
- EU digital education
- research projects
- education projects
- development projects


NEWSLETTER-WORTHY CONTENT
- important new reports
- research
- studies
- surveys
- funding opportunities
- grants
- education events
- webinars
- seminars
- conferences
- new tools
- new platforms
- important technology releases
- major policy changes
- experimental technologies
- emerging trends
- weak signals about the future of education or working life


--------------------------------------------------

RELEVANCE SCALE

1 = Completely unrelated.

Examples:
politics with no connection to education or working life,
sports, entertainment, crime, celebrity news.


2 = Weak connection.

The article mentions technology, education or work,
but contains little that would be useful for the organization's members.


3 = Potentially relevant.

There is a meaningful connection to education, learning,
technology, competence or working life.

A human should review the article.


4 = Clearly relevant.

The article contains information that professionals working
with digital learning, education technology, AI, competence
development or working life could reasonably find useful.


5 = Highly relevant.

The article directly concerns areas such as digital learning,
educational technology, AI in education, major education research,
important digital education policy, significant funding opportunities,
or major developments affecting education and learning.


IMPORTANT SCORING RULE:

Do NOT give an article a score of 1 simply because it is not specifically
about e-learning.

Education, teaching, learning, schools, universities, skills development,
AI, technology and working-life changes can all be relevant.

If an article is clearly about education or learning,
it should normally receive at least 3 unless it has no useful connection
to the organization's activities.


--------------------------------------------------

SUMMARY RULES

Use ONLY the information contained in the article title and description.

Do not invent information.

Do not add facts that are not provided.

Write all Finnish text in fluent and natural standard Finnish.

Avoid literal word-for-word translation.

Write in concise professional Finnish suitable for a member newsletter.


--------------------------------------------------

Return ONLY valid JSON.

Use exactly this structure:

{{
    "relevance": 1,
    "reason_fi": "Lyhyt perustelu sille, miksi sisältö on tai ei ole relevantti.",
    "summary_fi": "Selkeä ja luonnollinen 2–3 virkkeen suomenkielinen yhteenveto.",
    "topics": [
        "aihe 1",
        "aihe 2"
    ],
    "newsletter_recommendation": false
}}


ARTICLE INFORMATION

Source:
{source_name}

Title:
{title}

Description:
{description}

Link:
{link}
"""

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

    response_data = response.json()
    ai_text = response_data["response"]

    return json.loads(ai_text)


# --------------------------------------------------
# START
# --------------------------------------------------

print()
print("=" * 70)
print("STARTING RSS ANALYSIS")
print("=" * 70)
print()


# --------------------------------------------------
# LOOP THROUGH SOURCES
# --------------------------------------------------

for source in rss_sources:

    print()
    print("=" * 70)
    print("SOURCE:", source["name"])
    print("=" * 70)

    feed = feedparser.parse(source["url"])

    if feed.bozo:
        print("⚠️ Feed warning:", feed.bozo_exception)

    print("Feed title:", feed.feed.get("title", source["name"]))
    print("Entries available in feed:", len(feed.entries))

    articles_to_analyze = feed.entries[:number_of_articles]

    print("Articles to analyze:", len(articles_to_analyze))
    print()


    # --------------------------------------------------
    # LOOP THROUGH ARTICLES
    # --------------------------------------------------

    for index, article in enumerate(articles_to_analyze, start=1):

        title = article.get("title", "No title")
        link = article.get("link", "No link")

        description = article.get("summary", "")

        if not description:
            description = article.get("description", "")

        print("-" * 70)
        print(f"Article {index}/{len(articles_to_analyze)}")
        print("Source:", source["name"])
        print("Title:", title)
        print("Link:", link)


        # --------------------------------------------------
        # AI ANALYSIS
        # --------------------------------------------------

        try:

            analysis = analyze_article(
                source["name"],
                title,
                description,
                link
            )

            relevance = analysis.get("relevance", 1)
            reason = analysis.get("reason_fi", "")
            summary = analysis.get("summary_fi", "")
            topics = analysis.get("topics", [])

            newsletter_recommendation = analysis.get(
                "newsletter_recommendation",
                False
            )

            result = {
                "source": source["name"],
                "title": title,
                "link": link,
                "relevance": relevance,
                "reason": reason,
                "summary": summary,
                "topics": topics,
                "newsletter_recommendation": newsletter_recommendation
            }

            print()
            print("Relevance:", relevance)
            print("Topics:", ", ".join(topics))
            print("Reason:", reason)
            print("Summary:", summary)
            print(
                "Newsletter recommendation:",
                newsletter_recommendation
            )

            if relevance >= 4:

                kept_articles.append(result)

                print()
                print("✅ KEEP ARTICLE")

            elif relevance == 3:

                review_articles.append(result)

                print()
                print("🟡 REVIEW ARTICLE")

            else:

                ignored_articles.append(result)

                print()
                print("❌ IGNORE ARTICLE")


        except requests.exceptions.RequestException as error:

            print()
            print("❌ Error connecting to Ollama:")
            print(error)


        except json.JSONDecodeError as error:

            print()
            print("❌ AI returned invalid JSON:")
            print(error)


        except Exception as error:

            print()
            print("❌ Unexpected error:")
            print(error)


        print()


# --------------------------------------------------
# FINAL RESULTS
# --------------------------------------------------

print()
print("=" * 70)
print("FINAL RESULTS")
print("=" * 70)

total_checked = (
    len(kept_articles)
    + len(review_articles)
    + len(ignored_articles)
)

print()
print("Checked articles:", total_checked)
print("Relevant articles:", len(kept_articles))
print("Articles for review:", len(review_articles))
print("Ignored articles:", len(ignored_articles))


# --------------------------------------------------
# RELEVANT ARTICLES
# --------------------------------------------------

print()
print("=" * 70)
print("✅ RELEVANT ARTICLES")
print("=" * 70)

if not kept_articles:
    print("No relevant articles found.")

for article in kept_articles:

    print()
    print("Source:", article["source"])
    print("Title:", article["title"])
    print("Relevance:", article["relevance"])
    print("Topics:", ", ".join(article["topics"]))
    print("Reason:", article["reason"])
    print("Summary:", article["summary"])
    print("Link:", article["link"])

 
# --------------------------------------------------
# REVIEW ARTICLES
# --------------------------------------------------

print()
print("=" * 70)
print("🟡 ARTICLES FOR REVIEW")
print("=" * 70)

if not review_articles:
    print("No articles require review.")

for article in review_articles:

    print()
    print("Source:", article["source"])
    print("Title:", article["title"])
    print("Relevance:", article["relevance"])
    print("Topics:", ", ".join(article["topics"]))
    print("Reason:", article["reason"])
    print("Summary:", article["summary"])
    print("Link:", article["link"])


# --------------------------------------------------
# IGNORED ARTICLES
# --------------------------------------------------

print()
print("=" * 70)
print("❌ IGNORED ARTICLES")
print("=" * 70)

if not ignored_articles:
    print("No ignored articles.")

for article in ignored_articles:

    print()
    print("Source:", article["source"])
    print("Title:", article["title"])
    print("Relevance:", article["relevance"])
    print("Reason:", article["reason"])
    print("Link:", article["link"])
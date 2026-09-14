import requests
import json


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "qwen2.5:7b"


def analyze_article(article):
    """
    Analyze one article using Ollama + Qwen.

    Expects article to contain:
    - source
    - title
    - link
    - description

    Returns a dictionary containing:
    - source
    - title
    - link
    - relevance
    - reason
    - summary
    - topics
    - newsletter_recommendation
    """

    source = article.get(
        "source",
        "Unknown source"
    )

    title = article.get(
        "title",
        "No title"
    )

    link = article.get(
        "link",
        ""
    )

    description = article.get(
        "description",
        ""
    )

    prompt = f"""
You are an information monitoring assistant for Suomen eOppimiskeskus ry.

Your task is to decide whether an article could be useful for the
organization, its members, or its member newsletter.

The article does NOT need to mention Suomen eOppimiskeskus ry directly.

An article can be relevant if it discusses developments, research,
technology, policy, tools, projects, events or trends that could be
interesting to professionals working with education, learning,
digitalization or competence development.


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


RELEVANCE SCALE

1 = Completely unrelated.

Examples:
politics with no connection to education or working life,
sports, entertainment, crime or celebrity news.


2 = Weak connection.

The article mentions technology, education or work,
but contains little that would be useful for the organization's members.


3 = Potentially relevant.

There is a meaningful connection to education, learning,
technology, competence or working life.

A human should review the article.


4 = Clearly relevant.

The article contains information that professionals working
with digital learning, educational technology, AI,
competence development or working life could reasonably find useful.


5 = Highly relevant.

The article directly concerns areas such as digital learning,
educational technology, AI in education, major education research,
important digital education policy, significant funding opportunities,
or major developments affecting education and learning.


IMPORTANT SCORING RULES

Do NOT give an article a score of 1 simply because it is not specifically
about e-learning.

Education, teaching, learning, schools, universities,
skills development, AI, technology and working-life changes
can all be relevant.

If an article is clearly about education or learning,
it should normally receive at least 3 unless it has no useful connection
to the organization's activities.


SUMMARY RULES

Use ONLY the information contained in the title and description below.

Do not invent information.

Do not add facts that are not provided.

Write all Finnish text in fluent and natural standard Finnish.

Avoid literal word-for-word translation.

Write concise professional Finnish suitable for a member newsletter.


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
{source}

Title:
{title}

Description:
{description}

Link:
{link}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
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

        ai_text = response_data[
            "response"
        ]

        analysis = json.loads(
            ai_text
        )

        result = {
            "source": source,
            "title": title,
            "link": link,
            "relevance": analysis.get(
                "relevance",
                1
            ),
            "reason": analysis.get(
                "reason_fi",
                ""
            ),
            "summary": analysis.get(
                "summary_fi",
                ""
            ),
            "topics": analysis.get(
                "topics",
                []
            ),
            "newsletter_recommendation":
                analysis.get(
                    "newsletter_recommendation",
                    False
                )
        }

        return result

    except requests.exceptions.RequestException as error:
        return {
            "source": source,
            "title": title,
            "link": link,
            "relevance": 0,
            "reason": (
                "Could not connect to Ollama."
            ),
            "summary": "",
            "topics": [],
            "newsletter_recommendation": False,
            "error": str(error)
        }

    except json.JSONDecodeError as error:
        return {
            "source": source,
            "title": title,
            "link": link,
            "relevance": 0,
            "reason": (
                "The AI returned invalid JSON."
            ),
            "summary": "",
            "topics": [],
            "newsletter_recommendation": False,
            "error": str(error)
        }

    except Exception as error:
        return {
            "source": source,
            "title": title,
            "link": link,
            "relevance": 0,
            "reason": (
                "Unexpected error during analysis."
            ),
            "summary": "",
            "topics": [],
            "newsletter_recommendation": False,
            "error": str(error)
        }


if __name__ == "__main__":
    test_article = {
        "source": "Test source",
        "title": (
            "Artificial intelligence is changing "
            "digital learning"
        ),
        "link": "https://example.com",
        "description": (
            "A new study examines how teachers "
            "are using artificial intelligence "
            "tools in online education."
        )
    }

    result = analyze_article(
        test_article
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )
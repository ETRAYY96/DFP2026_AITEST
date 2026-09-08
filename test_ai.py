import requests

article = """
Artificial intelligence is becoming increasingly common in education.
Teachers are using AI tools to create learning materials, provide feedback
and reduce repetitive administrative tasks. Researchers have also emphasized
the importance of teaching students how to use AI responsibly.
"""

prompt = f"""
You are an information assistant for Suomen eOppimiskeskus ry.

The organization is interested in topics such as:
- digital learning
- artificial intelligence in education
- educational technology
- digital skills
- accessibility
- future skills
- changes in working life

Analyze the following article.

ARTICLE:
{article}

Return:

TITLE:
SUMMARY:
RELEVANCE: (1-5)
REASON:
TOPICS:
NEWSLETTER_RECOMMENDATION: (YES or NO)

Write the summary and reason in Finnish.
"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False
    }
)

print(response.json()["response"])
"""
Newsletter Draft Generator
---------------------------
Matches the client's (Finnish e-learning association) actual workflow:
  - They gather info from web pages / social posts about EVENTS and FIELD HIGHLIGHTS
  - They currently post interesting finds to a Telegram channel, then manually
    decide what to include in the newsletter
  - This script automates the "summarize" step: give it a list of links,
    it produces a short, original summary for each (not a copy of the source),
    plus the source link, organized by section (Events / Field Highlights)
  - Uses qwen2.5:7b via Ollama, running fully locally -> no per-request cost

Run locally (requires Ollama running: `ollama serve` in a separate terminal):
    python3 newsletter_generator.py
"""

import requests
from newspaper import Article


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:7b"

# Anti-hallucination, copyright-safe instructions:
# - "in your own words" -> avoids copying source text directly (copyright)
# - "only use facts explicitly stated" -> reduces hallucination risk
# - short length -> keeps it a newsletter blurb, not a reproduction
SUMMARY_INSTRUCTION = (
    "Summarise this in 2-3 sentences, in your own words, suitable for a "
    "newsletter blurb. Only use facts explicitly stated in the article "
    "above. Do not invent names, numbers, or details that are not in "
    "the text. Do not copy sentences directly from the article - "
    "rewrite in your own words."
)


def get_article_text(url):
    """Download and extract the readable text of an article from a URL."""
    article = Article(url)
    article.download()
    article.parse()
    return article.title, article.text


def summarise_with_qwen(title, text):
    """Two-step chat: send article as context, then ask for a summary."""
    # Trim very long articles - smaller local models are less reliable
    # on very long inputs (we saw this cause hallucination in testing)
    max_chars = 6000
    trimmed_text = text[:max_chars]

    messages = [
        {"role": "user", "content": f"Title: {title}\n\nArticle: {trimmed_text}"},
        {"role": "user", "content": SUMMARY_INSTRUCTION},
    ]

    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "messages": messages, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()


def build_newsletter_section(section_title, links):
    """Process a list of links into one newsletter section (e.g. 'Events')."""
    print(f"\n--- Processing section: {section_title} ---")
    entries = []

    for url in links:
        try:
            print(f"Downloading: {url}")
            title, text = get_article_text(url)

            if not text or len(text) < 200:
                print(f"  Skipped (too little text extracted): {url}")
                continue

            print("  Summarising...")
            summary = summarise_with_qwen(title, text)

            entries.append({
                "title": title,
                "summary": summary,
                "source_url": url,
            })
            print("  Done.")

        except Exception as e:
            print(f"  Failed to process {url}: {e}")

    return {"section_title": section_title, "entries": entries}


def format_newsletter_markdown(sections):
    """Turn the processed sections into a readable draft, ready for human review."""
    lines = ["# Newsletter Draft (AI-generated - please review before sending)\n"]

    for section in sections:
        lines.append(f"## {section['section_title']}\n")
        if not section["entries"]:
            lines.append("_No items processed for this section._\n")
            continue

        for entry in section["entries"]:
            lines.append(f"### {entry['title']}")
            lines.append(entry["summary"])
            lines.append(f"[Read more]({entry['source_url']})\n")

    return "\n".join(lines)


def format_newsletter_html(sections, newsletter_title="Association Newsletter"):
    """Turn the processed sections into a styled HTML newsletter, viewable in any browser."""

    def entry_html(entry):
        return f"""
        <div class="entry">
          <h3>{entry['title']}</h3>
          <p>{entry['summary']}</p>
          <a class="read-more" href="{entry['source_url']}" target="_blank">Read the full source &rarr;</a>
        </div>"""

    def section_html(section):
        if not section["entries"]:
            body = '<p class="empty">No items in this section yet.</p>'
        else:
            body = "".join(entry_html(e) for e in section["entries"])
        return f"""
      <section>
        <div class="section-label">{section['section_title']}</div>
        {body}
      </section>"""

    sections_markup = "".join(section_html(s) for s in sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{newsletter_title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600&family=Inter:wght@400;500&display=swap');

  body {{
    margin: 0;
    padding: 48px 20px;
    background: #EFEAE0;
    font-family: 'Inter', sans-serif;
    color: #1F2A24;
  }}

  .newsletter {{
    max-width: 620px;
    margin: 0 auto;
    background: #FBFAF7;
    padding: 48px 44px;
    border: 1px solid #DCD7CA;
  }}

  .masthead {{
    text-align: left;
    border-bottom: 2px solid #2F6F62;
    padding-bottom: 20px;
    margin-bottom: 36px;
  }}

  .masthead h1 {{
    font-family: 'Lora', serif;
    font-weight: 600;
    font-size: 28px;
    margin: 0 0 6px 0;
    color: #1F2A24;
  }}

  .masthead .note {{
    font-size: 13px;
    color: #6B7268;
  }}

  section {{
    margin-bottom: 40px;
  }}

  .section-label {{
    font-family: 'Lora', serif;
    font-size: 15px;
    font-weight: 600;
    color: #C98A3E;
    margin-bottom: 18px;
    padding-bottom: 8px;
    border-bottom: 1px solid #DCD7CA;
  }}

  .entry {{
    margin-bottom: 26px;
  }}

  .entry:last-child {{
    margin-bottom: 0;
  }}

  .entry h3 {{
    font-family: 'Lora', serif;
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: #1F2A24;
    line-height: 1.35;
  }}

  .entry p {{
    font-size: 15px;
    line-height: 1.6;
    margin: 0 0 10px 0;
    color: #2E362F;
  }}

  .read-more {{
    font-size: 13px;
    color: #2F6F62;
    text-decoration: none;
    font-weight: 500;
  }}

  .read-more:hover {{
    text-decoration: underline;
  }}

  .empty {{
    font-size: 14px;
    color: #6B7268;
    font-style: italic;
  }}

  .footer-note {{
    margin-top: 36px;
    padding-top: 20px;
    border-top: 1px solid #DCD7CA;
    font-size: 12px;
    color: #6B7268;
  }}
</style>
</head>
<body>
  <div class="newsletter">
    <div class="masthead">
      <h1>{newsletter_title}</h1>
      <div class="note">AI-assisted draft &mdash; please review before sending</div>
    </div>
    {sections_markup}
    <div class="footer-note">
      Summaries generated locally with qwen2.5:7b via Ollama. Each item links back to its original source.
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    # --- EDIT THESE: replace with real links your team gathers each cycle ---
    events_links = [
        # "https://example.com/some-upcoming-event",
    ]

    field_highlight_links = [
        "https://www.hamk.fi/julkaisut/opiskeluhyvinvointi-ammattikorkeakoulussa-opiskelijoiden-kokemuksia-voimavaroista-ja-vaatimuksista/",
    ]
    # --------------------------------------------------------------------

    sections = [
        build_newsletter_section("Events", events_links),
        build_newsletter_section("Field Highlights", field_highlight_links),
    ]

    draft = format_newsletter_markdown(sections)

    print("\n\n=== FULL NEWSLETTER DRAFT ===\n")
    print(draft)

    with open("newsletter_draft.md", "w") as f:
        f.write(draft)
    print("\nSaved to newsletter_draft.md - open it, review, and edit before sending.")

    html_draft = format_newsletter_html(sections)
    with open("newsletter_draft.html", "w") as f:
        f.write(html_draft)
    print("Saved to newsletter_draft.html - open this one in a browser to see the visual version.")
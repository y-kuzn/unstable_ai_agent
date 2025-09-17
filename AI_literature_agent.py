import streamlit as st
import requests
import json
import re
import time
from bs4 import BeautifulSoup
from pyzotero import zotero
import fitz  # PyMuPDF

# ---------------------------
# Configuration
# ---------------------------
SCRAPERAPI_KEY = st.secrets["SCRAPERAPI_KEY"]
SEMANTIC_SCHOLAR_API_KEY = st.secrets["SEMANTIC_SCHOLAR_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# ---------------------------
# UI Inputs
# ---------------------------
st.set_page_config(page_title="📚 AI Literature Helper", page_icon="🤖")
st.title("📚 AI Literature Helper")

search_mode = st.radio("🔍 Search Mode", ["Keyword Search", "Exact Paper Lookup"])
search_source = st.selectbox("📡 Choose search source", ["Google Scholar", "Semantic Scholar"])
max_results = st.slider("📄 Max articles to fetch:", 5, 50, 10, 1)
min_score = st.slider("⭐ Minimum AI relevance score to save to Zotero (0–5):", 0.0, 5.0, 3.0, 0.1)
allow_duplicates = st.checkbox("⚠️ Allow Zotero duplicates")

if search_mode == "Exact Paper Lookup":
    exact_input = st.text_input("📄 Enter exact paper title or DOI")
else:
    user_prompt = st.text_input("🔍 Enter your research topic or keywords:")

add_to_zotero = st.checkbox("📥 Add articles to Zotero")
user_zotero_key = user_zotero_id = user_zotero_collection = ""

if add_to_zotero:
    st.markdown("### 🔐 Zotero Credentials")
    user_zotero_key = st.text_input("Zotero API Key")
    user_zotero_id = st.text_input("Zotero User ID")
    user_zotero_collection = st.text_input("Zotero Collection ID")

# ---------------------------
# Helper Functions
# ---------------------------
def generate_gemini(prompt_text):
    headers = {"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY}
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    resp = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

def extract_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"tags": [], "summary": "", "score": 0.0, "reasoning": ""}

def search_google_scholar(query, num_results=10):
    url = "https://api.scraperapi.com/"
    params = {
        "api_key": SCRAPERAPI_KEY,
        "url": f"https://scholar.google.com/scholar?q={query.replace(' ','+')}"
    }
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for entry in soup.select(".gs_ri")[:num_results]:
        title_tag = entry.select_one(".gs_rt a")
        title = title_tag.text if title_tag else entry.select_one(".gs_rt").text
        url = title_tag["href"] if title_tag else ""
        authors_info = entry.select_one(".gs_a").text if entry.select_one(".gs_a") else ""
        snippet = entry.select_one(".gs_rs").text if entry.select_one(".gs_rs") else ""
        results.append({
            "title": title,
            "url": url,
            "authors_info": authors_info,
            "snippet": snippet,
            "pdf_url": ""
        })
    return results

def search_semantic_scholar(query, limit=10):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY}
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,url,abstract,openAccessPdf"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    results = []
    for paper in data.get("data", []):
        results.append({
            "title": paper.get("title", ""),
            "url": paper.get("url", ""),
            "authors_info": ", ".join([a.get("name", "") for a in paper.get("authors", [])]),
            "snippet": paper.get("abstract", ""),
            "pdf_url": paper.get("openAccessPdf", {}).get("url", "")
        })
    return results

def parse_authors(authors_info):
    authors = [a.strip() for a in authors_info.split(",") if a.strip()]
    parsed = []
    for name in authors:
        parts = name.split(" ")
        if len(parts) >= 2:
            parsed.append({
                "creatorType": "author",
                "firstName": " ".join(parts[:-1]),
                "lastName": parts[-1]
            })
    return parsed

def extract_pdf_text(url):
    try:
        response = requests.get(url)
        with open("temp.pdf", "wb") as f:
            f.write(response.content)
        doc = fitz.open("temp.pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text[:3000]
    except:
        return ""

def format_bibtex(item):
    authors = " and ".join([f"{a['lastName']}, {a['firstName']}" for a in item['creators']])
    return f"""@article{{{item['title'].replace(' ', '_')},
    title={{ {item['title']} }},
    author={{ {authors} }},
    journal={{AI Literature Helper}},
    year={{2025}},
    url={{ {item['url']} }},
    abstract={{ {item['abstractNote']} }}
  }}"""

def format_markdown(item):
    authors = ", ".join([f"{a['firstName']} {a['lastName']}" for a in item['creators']])
    return f"- **{item['title']}** by {authors}. [Link]({item['url']})\n  > {item['abstractNote']}"

# ---------------------------
# Main Logic
# ---------------------------
if st.button("🚀 Fetch & Analyze Articles"):
    papers_meta = []

    if search_mode == "Exact Paper Lookup":
        if not exact_input.strip():
            st.warning("Please enter a paper title or DOI.")
            st.stop()

        doi_pattern = r"10.\d{4,9}/[-._;()/:A-Z0-9]+"
        is_doi = bool(re.search(doi_pattern, exact_input, re.IGNORECASE))

        st.info(f"🔎 Looking up {'DOI' if is_doi else 'title'}...")
        try:
            headers = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY}
            if is_doi:
                url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{exact_input}"
                params = {"fields": "title,authors,url,abstract,openAccessPdf"}
                response = requests.get(url, headers=headers, params=params)
                paper = response.json()
                papers_meta = [{
                    "title": paper.get("title", ""),
                    "url": paper.get("url", ""),
                    "authors_info": ", ".join([a.get("name", "") for a in paper.get("authors", [])]),
                    "snippet": paper.get("abstract", ""),
                    "pdf_url": paper.get("openAccessPdf", {}).get("url", "")
                }]
            else:
                papers_meta = search_semantic_scholar(exact_input, limit=1)
        except Exception as e:
            st.error(f"Search error: {e}")
            papers_meta = []

    else:
        if not user_prompt.strip():
            st.warning("Please enter a research topic.")
            st.stop()
        st.info(f"🔎 Searching {search_source}...")
        try:
            if search_source == "Google Scholar":
                papers_meta = search_google_scholar(user_prompt, num_results=max_results)
            else:
                papers_meta = search_semantic_scholar(user_prompt, limit=max_results)
        except Exception as e:
            st.error(f"Search error: {e}")
            papers_meta = []

    if add_to_zotero and user_zotero_key and user_zotero_id:
        try:
            zot = zotero.Zotero(user_zotero_id, 'user', user_zotero_key)
        except Exception as e:
            st.error(f"Zotero initialization error: {e}")
            zot = None
    else:
        zot = None

    for paper in papers_meta:
        title = paper.get("title", "")
        url = paper.get("url", "")
        authors_info = paper.get("authors_info", "")
        snippet = paper.get("snippet", "")
        pdf_url = paper.get("pdf_url", "")
        pdf_text = extract_pdf_text(pdf_url or url)

        st.markdown(f"### 📄 Preview: {title or 'Untitled'}")
        st.markdown(f"**Authors:** {authors_info or 'N/A'}")
        st.markdown(f"**Abstract:** {snippet or 'No abstract available.'}")
        st.markdown(f"[🔗 View Paper]({url})")
        st.markdown("---")

        gemini_prompt = f"""
        Article Title: {title}
        Authors info: {authors_info}
        Abstract/Snippet: {snippet}
        PDF Text (if available): {pdf_text}
        URL: {url}

        Based on the research topic: '{user_prompt if search_mode == 'Keyword Search' else exact_input}', generate:
        1. 3–5 descriptive tags
        2. A short 10 sentence summary, highlighting the journal prestige, authors visibility and overall relevance to set query
        3. Relevance score 0–5 (float)
        4. Reasoning for the score
        Output as JSON with keys: tags, summary, score, reasoning
        """

        try:
            text_output = generate_gemini(gemini_prompt)
            gpt_data = extract_json(text_output)
            tags = gpt_data.get("tags", [])
            summary = gpt_data.get("summary", "")
            score = float(gpt_data.get("score", 0))
            reasoning = gpt_data.get("reasoning", "")
        except Exception as e:
            st.error(f"Gemini API error: {e}")
            tags, summary, score, reasoning = [], "", 0.0, ""

        st.markdown(f"**🔢 AI Relevance Score:** {score:.2f}")
        st.markdown(f"**🧠 Gemini Reasoning:** {reasoning}")
        if tags:
            st.markdown("**🏷️ Tags:** " + ", ".join(tags))

        # Export options
        if title and title.strip():
            st.download_button(
                "📥 Export BibTeX",
                format_bibtex({
                    'title': title,
                    'creators': parse_authors(authors_info),
                    'abstractNote': summary,
                    'url': url
                }),
                file_name=f"{title.replace(' ', '_')}.bib"
            )

            st.download_button(
                "📥 Export Markdown",
                format_markdown({
                    'title': title,
                    'creators': parse_authors(authors_info),
                    'abstractNote': summary,
                    'url': url
                }),
                file_name=f"{title.replace(' ', '_')}.md"
            )
        else:
            st.warning("⚠️ Cannot export bibliographic data: missing article title.")

        st.markdown("---")

        # Zotero logic
        if score >= min_score and add_to_zotero and zot and user_zotero_collection:
            item = {
                'itemType': 'journalArticle',
                'title': title,
                'creators': parse_authors(authors_info),
                'abstractNote': summary,
                'tags': [{'tag': t} for t in tags],
                'url': url,
                'collections': [user_zotero_collection]
            }

            duplicate_found = False
            try:
                existing_items = zot.items(q=title, itemType="journalArticle")
                for existing in existing_items:
                    if "title" in existing["data"] and existing["data"]["title"].strip().lower() == title.strip().lower():
                        duplicate_found = True
                        break
            except Exception as e:
                st.warning(f"⚠️ Zotero duplicate check failed: {e}")

            if duplicate_found and not allow_duplicates:
                st.warning(f"⚠️ Skipped Zotero save: duplicate found for '{title}'")
            else:
                try:
                    zot.create_items([item])
                    st.success(f"✅ Added to Zotero (score {score:.2f})")
                except Exception as e:
                    st.error(f"❌ Zotero error: {e}")

st.markdown("""
<style>
.help-button {
    display: inline-block;
    padding: 0.6em 1.2em;
    font-size: 1.1em;
    font-weight: 600;
    color: black;  /* 👈 Black text */
    background-color: #f0f0f0;
    border: 2px solid black;
    border-radius: 8px;
    text-decoration: none;  /* 👈 Removes underline */
    transition: all 0.3s ease;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}
.help-button:hover {
    background-color: #e0e0e0;
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}
</style>

<div style='text-align: center; margin-top: 50px;'>
    <a href='https://ntu-ai-literature-search-question.streamlit.app/' target='_blank' class='help-button'>
        🆘 Visit Help Page
    </a>
</div>
""", unsafe_allow_html=True)

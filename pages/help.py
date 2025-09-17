import streamlit as st

# Page setup
st.set_page_config(page_title="AI Literature Helper – Help", page_icon="🆘", layout="wide")

# Sidebar navigation
st.sidebar.title("📘 Help Navigation")
section = st.sidebar.radio("Jump to section:", [
    "Overview",
    "How to Use",
    "Zotero Integration",
    "Gemini API Errors",
    "Run Locally with Personal APIs",
    "Contact"
])
st.sidebar.markdown("---")

st.sidebar.markdown("""
<div style="text-align: center;">
    <a href="https://ai-literature-search.streamlit.app/" target="_blank">
        <button style="
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            margin-top: 10px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        ">
            🔙 Go Back to Main App
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

# Section: Overview
if section == "Overview":
    st.title("🆘 Help & Instructions")
    st.markdown("""
    Welcome to **AI Literature Helper**, your personal research assistant powered by Gemini and Streamlit.

    This app helps you:
    - Search academic papers from Google Scholar or Semantic Scholar
    - Analyze relevance using Gemini AI
    - Export citations in BibTeX or Markdown
    - Save papers directly to Zotero

    Whether you're a student, researcher, or curious mind, this tool is designed to streamline your literature review process.
    """)

# Section: How to Use
elif section == "How to Use":
    st.header("🚀 How to Use the App")
    st.markdown("""
    1. **Enter your research topic** in the input field.
    2. **Choose a source**: Google Scholar or Semantic Scholar.
    3. **Set the number of papers** to fetch and your minimum relevance score.
    4. **Optionally connect Zotero** to save papers directly to your library.
    5. Click **Fetch & Analyze Articles** to begin.

    After analysis, you’ll see:
    - AI-generated tags
    - Summary and relevance score
    - Export buttons for BibTeX and Markdown
    """)

# Section: Zotero Integration
elif section == "Zotero Integration":
    st.header("📥 Zotero Integration")
    st.markdown("""
    Zotero is a free reference manager. You can connect it to this app to automatically save relevant papers.

    ### 🔧 What You Need
    - **Zotero API Key**: [Generate here](https://www.zotero.org/settings/keys)
    - **User ID**: Found in your Zotero account settings
    - **Collection ID**: Go to your Zotero library → right-click a collection → “Edit Collection” → copy the ID from the URL

    ### 📝 Add to Secrets
    ```toml
    ZOTERO_API_KEY = "your_zotero_key"
    ZOTERO_USER_ID = "your_user_id"
    ZOTERO_COLLECTION_ID = "your_collection_id"
    ```

    ### ✅ What Gets Saved
    - Only papers with a relevance score ≥ your threshold
    - Includes title, authors, abstract, tags, and URL

    > ⚠️ Zotero does not accept empty fields. Make sure your metadata is complete.
    """)

# Section: Gemini API Errors
elif section == "Gemini API Errors":
    st.header("⚠️ Gemini API Errors & What They Mean")
    st.markdown("""
    Sometimes you may see errors when the app calls the Gemini API. Here are the most common ones:

    - **400 – INVALID_ARGUMENT**: The request was malformed (e.g. missing fields or wrong format).  
      ➡️ Check your input and try again.

    - **400 – FAILED_PRECONDITION**: Free tier not available in your region.  
      ➡️ Enable billing in Google AI Studio to continue.

    - **403 – PERMISSION_DENIED**: Your API key doesn’t have the right permissions.  
      ➡️ Verify you’re using the correct key with proper access.

    - **404 – NOT_FOUND**: The requested resource wasn’t found.  
      ➡️ Double-check the model name or resource.

    - **429 – RESOURCE_EXHAUSTED**: You’ve hit the rate limit.  
      ➡️ Slow down requests or request a quota increase.

    - **500 – INTERNAL**: Unexpected server error (often due to too much input).  
      ➡️ Try reducing input size or switching to a lighter model.

    - **503 – UNAVAILABLE**: The service is temporarily overloaded.  
      ➡️ Wait a few minutes and retry.

    For more details, see Google’s [Gemini API troubleshooting guide](https://ai.google.dev/gemini-api/docs/troubleshooting).
    """)

# Section: Run Locally with Personal APIs
elif section == "Run Locally with Personal APIs":
    st.header("💻 Run Locally with Your Own API Keys")
    st.markdown("""
    While this hosted version is convenient, you may encounter rate limits or shared quota issues.  
    The best way to get a smooth experience is to **run the helper locally** with your own API keys.

    ### 🚀 Why Run Locally?
    - Full control over your API usage and quotas
    - No risk of hitting shared limits
    - Better privacy: your keys and data stay on your machine
    - Ability to customize the app for your workflow

    ### 🔧 How to Do It
    1. Clone the GitHub repository:
       ```bash
       git clone https://github.com/y-kuzn/ai_lit_agent.git
       cd ai_lit_agent
       ```
    2. Install dependencies:
       ```bash
       pip install -r requirements.txt
       ```
    3. Create a `.streamlit/secrets.toml` file with your own keys:
       ```toml
       SCRAPERAPI_KEY = "your_scraperapi_key"
       SEMANTIC_SCHOLAR_API_KEY = "your_semantic_key"
       GEMINI_API_KEY = "your_gemini_key"
       ZOTERO_API_KEY = "your_zotero_key"
       ZOTERO_USER_ID = "your_user_id"
       ZOTERO_COLLECTION_ID = "your_collection_id"
       ```
    4. Run the app:
       ```bash
       streamlit run lit_enhanced.py
       ```

    👉 This way, you’ll have a **faster, more reliable, and private** research assistant.
    """)

# Section: Contact
elif section == "Contact":
    st.header("📬 Contact & Feedback")
    st.markdown("""
    Have questions, suggestions, or found a bug?

    - Open an issue on [GitHub](https://github.com/y-kuzn/ai_lit_agent/issues)
    - Email the developer at: `kuzn0001@e.ntu.edu.sg`
    - Or leave feedback directly in the app (coming soon!)

    We’re constantly improving the AI Literature Helper—your input helps make it better.
    """)

    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and Gemini")

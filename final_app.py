import streamlit as st
import google.generativeai as genai
import requests
import base64
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="GitGrade - AI Repo Analyzer", layout="wide")

st.title("GitGrade: AI-Powered Repository Analyzer 🚀")
st.markdown("### Unfold Success from Untold Experiences")
st.markdown("Evaluate your GitHub repository and get a **Score, Summary, and Personalized Roadmap.**")

# --- HELPER FUNCTIONS ---

def get_available_models(api_key):
    """Fetches available models that support content generation."""
    try:
        genai.configure(api_key=api_key)
        models = []
        for m in genai.list_models():
            # Only consider text-capable models for this task
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return models
    except Exception as e:
        # st.error(f"Error fetching models: {e}") # Suppress error in helper
        return []

def parse_github_url(url):
    """Extracts owner and repo name from a standard GitHub URL."""
    try:
        parts = url.rstrip("/").split("/")
        if len(parts) < 2:
            return None, None
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo
    except:
        return None, None

def fetch_file_content(owner, repo, file_path, token=None):
    """Fetches the content of a specific file using the GitHub Content API."""
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        
    file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    response = requests.get(file_url, headers=headers)
    
    if response.status_code == 200:
        content_b64 = response.json().get('content', '')
        try:
            return base64.b64decode(content_b64).decode('utf-8')
        except:
            return f"Error decoding {file_path} content."
    return f"File {file_path} not found or inaccessible."


def get_repo_structure(owner, repo, token=None):
    """Fetches metadata, file tree, README, and dependency files (V1 feature)."""
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    # 1. Get Repository Metadata
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        error_message = response.json().get('message', 'Unknown error')
        return None, f"Error: Could not fetch repo. Status Code: {response.status_code}. Message: {error_message}"
    
    repo_data = response.json()
    default_branch = repo_data.get("default_branch", "main")
    
    # 2. Get File Tree (Recursive)
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
    tree_response = requests.get(tree_url, headers=headers)
    
    file_structure = ""
    if tree_response.status_code == 200:
        tree_data = tree_response.json()
        files = [item['path'] for item in tree_data.get('tree', [])[:100]] 
        file_structure = "\n".join(files)

    # 3. Get README.md content 
    readme_content = fetch_file_content(owner, repo, "README.md", token)
    if "not found" in readme_content or "inaccessible" in readme_content:
        readme_content = "No README.md found."
    
    # 4. Dependency File Fetching (V1 feature)
    dependency_content = {}
    dep_files = ["requirements.txt", "package.json", "Pipfile", "pyproject.toml", "package-lock.json", "Pipfile.lock", "yarn.lock"]
    
    for file_name in dep_files:
        content = fetch_file_content(owner, repo, file_name, token)
        if "not found" not in content and "inaccessible" not in content:
            dependency_content[file_name] = content
            
    if not dependency_content:
        dependency_content["status"] = "No primary dependency file (e.g., requirements.txt, package.json) or lock file found."

    return {
        "metadata": repo_data,
        "structure": file_structure,
        "readme": readme_content,
        "dependencies": dependency_content 
    }, None

def analyze_with_gemini(repo_data, api_key, model_name):
    """Sends repo data to Gemini for analysis with enhanced Dependency Check (V1 prompt)."""
    try:
        genai.configure(api_key=api_key) 
        model = genai.GenerativeModel(model_name) 
    except Exception as e:
         return f"Error configuring Gemini API or loading model: {e}"

    # Format Dependency Data for the Prompt
    dep_summary = "\n\n".join([
        f"--- {name} ---\n{content}" for name, content in repo_data['dependencies'].items()
    ])

    # Construct the comprehensive prompt
    prompt = f"""
    You are a strict Senior Developer Mentor acting as an AI engine for "GitGrade".
    Your task is to evaluate a GitHub repository based on the following inputs:
    
    1. **Repository Metadata**: {repo_data['metadata']}
    2. **File Structure**: 
    {repo_data['structure']}
    3. **README Content**: 
    {repo_data['readme']}
    4. **Dependency Files Content**:
    {dep_summary}

    **Evaluation Criteria:**
    - **Code Quality & Organization:** Look for clean folder structures (src, tests, docs), separation of concerns.
    - **Documentation:** Is the README clear? Does it have setup instructions?
    - **Best Practices:** Presence of .gitignore, LICENSE, CI/CD workflows, test folders.
    - **Dependency Health (CRITICAL):** Analyze the provided dependency content (or lack thereof) for:
        a) **Security Risk:** Are common packages severely outdated? (Infer potential CVEs if versions are very old).
        b) **Maintainability:** Is a lock file (e.g., package-lock.json, Pipfile.lock) present? (Crucial for reproducible builds).
        c) **Clarity:** Are dependencies specified without version pinning? (Bad practice).

    **Output Requirement:**
    Provide the response in the following specific format:

    ### SCORE
    [Provide a score out of 100 based on the quality. Be honest and critical.]

    ### CRITICAL INSIGHTS
    [A 2-3 sentence section dedicated ONLY to Dependency Health and Security Risk. Be direct.]

    ### SUMMARY
    [A short paragraph (approx 50 words) evaluating the strengths and weaknesses of the overall project, including the Dependency Health findings.]

    ### ROADMAP
    [Bulleted list of 3-5 actionable steps the student must take to improve this project. Include at least two specific actions related to Dependency Health (e.g., pinning versions, adding a lock file, or updating a specific package).]
    
    Do not be polite just for the sake of it. Give honest, constructive feedback.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating content: {e}"

# --- SIDEBAR: DYNAMIC MODEL SELECTION (V2 Feature) ---
with st.sidebar:
    st.header("Configuration")
    
    # 1. Enter API Key
    gemini_api_key = st.text_input("1. Enter Gemini API Key", type="password")
    
    selected_model = None
    
    # 2. Dynamic Dropdown (Only appears if Key is valid)
    if gemini_api_key:
        with st.spinner("Fetching available models..."):
            available_models = get_available_models(gemini_api_key)
        
        if available_models:
            # Prefer 'flash' model for performance
            default_model = "models/gemini-2.5-flash"
            if default_model not in available_models:
                # Try 1.5-flash if 2.5 is unavailable
                default_model = "models/gemini-1.5-flash"

            try:
                default_ix = available_models.index(default_model)
            except ValueError:
                default_ix = 0 # Fallback to the first model

            selected_model = st.selectbox(
                "2. Select AI Model", 
                available_models, 
                index=default_ix
            )
            st.success(f"Connected! Using: **{selected_model.split('/')[-1]}**")
        else:
            st.error("Invalid Key or No Models Found.")
    else:
        st.warning("Please enter your Gemini API Key to select a model.")
    
    st.divider()
    github_token = st.text_input("3. GitHub Token (Optional)", type="password")
    st.info("A GitHub token is recommended to avoid GitHub API rate limits.")

# --- MAIN UI LOGIC ---

repo_url = st.text_input("Paste GitHub Repository URL", placeholder="https://github.com/username/project-name")

if st.button("Analyze Repository"):
    if not gemini_api_key:
        st.error("🚨 Please enter your Gemini API Key in the sidebar.")
    elif not selected_model:
        st.error("🚨 Please select an AI model from the sidebar.")
    elif not repo_url:
        st.error("Please enter a GitHub URL.")
    else:
        owner, repo = parse_github_url(repo_url)
        
        if not owner or not repo:
            st.error("Invalid GitHub URL format.")
        else:
            token_message = " (Using provided GitHub Token)" if github_token else " (May hit rate limits without a token)"
            
            with st.spinner(f"Fetching data for **{owner}/{repo}**...{token_message}"):
                repo_data, error = get_repo_structure(owner, repo, github_token)
            
            if error:
                st.error(error)
            else:
                st.success("Repository data fetched! Analyzing with Gemini AI...")
                
                with st.spinner(f"Generating Score, Summary, and Roadmap using **{selected_model.split('/')[-1]}**..."):
                    # Pass the selected model name to the analysis function
                    analysis = analyze_with_gemini(repo_data, gemini_api_key, selected_model)
                
                # --- DISPLAY RESULTS ---
                st.markdown("---")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=100)
                    st.metric(label="Repository", value=repo)
                    st.metric(label="Stars", value=repo_data['metadata'].get('stargazers_count', 0))
                
                with col2:
                    # Display the full analysis including CRITICAL INSIGHTS
                    st.markdown(analysis)

# --- FOOTER ---
st.markdown("---")
st.caption("Built for GitGrade Hackathon | Theme: AI + Code Analysis + Developer Profiling")
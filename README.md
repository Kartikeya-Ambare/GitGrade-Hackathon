# GitGrade: AI-Powered Repository Analyzer 🚀

**Unfold Success from Untold Experiences**

GitGrade is an intelligent GitHub repository analyzer that evaluates your projects and provides actionable insights, scores, and personalized roadmaps for improvement using Google's Gemini AI.

## 🌟 Features

- **Comprehensive Repository Analysis**: Fetches and analyzes repository metadata, file structure, README, and dependency files
- **AI-Powered Evaluation**: Uses Google Gemini 2.5 Flash for intelligent code quality assessment
- **Dependency Health Check**: Critical analysis of package versions, security risks, and maintainability
- **Actionable Roadmap**: Get personalized recommendations to improve your project
- **Score-Based Feedback**: Receive honest scoring out of 100 based on best practices
- **GitHub API Integration**: Optional token support to avoid rate limits

## 📋 Prerequisites

Before running GitGrade, ensure you have:

- Python 3.8 or higher
- A Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- (Optional) GitHub Personal Access Token for unlimited API requests

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/gitgrade.git
cd gitgrade
```

2. Install required dependencies:
```bash
pip install streamlit google-generativeai requests
```

3. Run the application:
```bash
streamlit run app.py
```

## 🔧 Configuration

### Required Setup

1. **Gemini API Key**: 
   - Obtain from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Currently hardcoded in the script (line 20) - **Important**: Replace with your own key or use environment variables for production

2. **GitHub Token** (Optional but Recommended):
   - Generate a personal access token from [GitHub Settings](https://github.com/settings/tokens)
   - Helps avoid API rate limits (60 requests/hour without token)

## 📖 Usage

1. Launch the Streamlit app
2. Enter your GitHub Personal Access Token in the sidebar (optional)
3. Paste a GitHub repository URL (e.g., `https://github.com/username/repo-name`)
4. Click **"Analyze Repository"**
5. Wait for the AI analysis to complete
6. Review your score, critical insights, summary, and improvement roadmap

## 🔍 What GitGrade Analyzes

### Code Quality & Organization
- Folder structure (src, tests, docs)
- Separation of concerns
- Project organization best practices

### Documentation
- README clarity and completeness
- Setup instructions
- Project description quality

### Best Practices
- Presence of `.gitignore`
- LICENSE file
- CI/CD workflows
- Test directories

### Dependency Health (Critical)
- **Security Risks**: Detection of outdated packages and potential CVEs
- **Maintainability**: Lock file presence (package-lock.json, Pipfile.lock)
- **Version Management**: Dependency version pinning practices

## 📊 Output Format

GitGrade provides structured feedback in four sections:

1. **SCORE**: A rating out of 100 based on comprehensive evaluation
2. **CRITICAL INSIGHTS**: Focused analysis on dependency health and security
3. **SUMMARY**: Overall project strengths and weaknesses (approx. 50 words)
4. **ROADMAP**: 3-5 actionable improvement steps with specific dependency recommendations

## 🛠️ Technical Details

### Supported Dependency Files
- `requirements.txt` (Python)
- `package.json` (Node.js)
- `package-lock.json` (Node.js lock file)
- `Pipfile` (Python - Pipenv)
- `Pipfile.lock` (Python - Pipenv lock)
- `pyproject.toml` (Python - Poetry)

### API Endpoints Used
- GitHub Repository API
- GitHub Contents API
- GitHub Git Trees API
- Google Gemini 2.5 Flash

## ⚠️ Important Notes

1. **API Key Security**: The Gemini API key is currently hardcoded. For production use:
   - Use environment variables
   - Use Streamlit secrets management
   - Never commit API keys to version control

2. **Rate Limits**: 
   - Without GitHub token: 60 requests/hour
   - With GitHub token: 5,000 requests/hour

3. **File Structure Limit**: Analyzes top 100 files to optimize API token usage

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🏆 Built For

GitGrade Hackathon | Theme: AI + Code Analysis + Developer Profiling

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ using Streamlit and Google Gemini AI**
# HireAI Talent Search Platform

A unified platform for natural language talent search, combining an LLM-powered NLP parser with dynamic data connectors.

## Project Structure

```
ai-hiring-copilot/
├── src/                                   # All source code
│   ├── parser/                            # Day 1: Natural Language Parser
│   │   ├── main.py
│   │   ├── ... (other parser files)
│   │
│   └── connectors/                        # Day 2+: Data Source Connectors
│       ├── github_agent/                  # GitHub Talent Search Agent
│       │   ├── main.py
│   │   │   ├── ... (other github agent files)
│   │   │
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── .env                                   # Environment variables (API keys)
├── main_app.py                            # Top-level FastAPI orchestrator
├── requirements.txt                       # Python dependencies
└── README.md                              # Project documentation
```

## Setup

1.  **Clone this repo:**
    ```bash
    git clone <your-repo-url>
    cd ai-hiring-copilot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables:**
    Create a file named `.env` in the **root directory** (`ai-hiring-copilot/`) and add your API keys:
    ```
    OPENROUTER_API_KEY=sk-or-v1-YOUR-OPENROUTER-API-KEY
    GITHUB_TOKEN=ghp_YOUR-GITHUB-PERSONAL-ACCESS-TOKEN
    ```
    *   **OpenRouter API Key:** Get this from [https://openrouter.ai/](https://openrouter.ai/)
    *   **GitHub Token:** Generate a [Personal Access Token (classic)](https://github.com/settings/tokens?type=classic) with `public_repo` and `read:user` scopes from your GitHub settings.

## Run the API

To run the combined FastAPI application:

```bash
uvicorn main_app:app --reload
```

Access the API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

*   **NLP Parser Endpoint:** `/nlp/parse-query`
*   **GitHub Search Endpoint:** `/github/search/github`
*   **Unified Talent Search Endpoint:** `/talent_search` (chains NLP to GitHub)

## Test with Sample Queries (CLI)

To test the full NLP -> GitHub pipeline via CLI:

```bash
python src/parser/test_queries.py
```

This script will:
1.  Take predefined sample natural language queries.
2.  Pass them to the NLP parser to get structured JSON.
3.  Use that structured JSON to search GitHub for matching candidate profiles.
4.  Print the resulting candidate profiles (including skills, activity, etc.). 
# Serbian News Helper
A smart AI assistant designed to fetch latest Montenegro news and transform them into interactive language study notes. This tool uses AI to analyze articles, identify key vocabulary, and provide linguistic context to help learners master the Serbian language.

## Features
- Automated News Scraping: Fetches the latest content from www.vijesti.me.

- AI-Powered Analysis: Generates summaries and identifies important vocabulary using Large Language Models.

- Linguistic Enrichment: Provides lemmas, parts of speech, and grammatical gender for nouns—critical for mastering Serbian declension.

# Tech Stack
Frontend: Streamlit

Package Manager: uv

Language Models: Integration with OpenAI

Data Source: Contemporary Serbian articles.

# Getting Started
## 1. Prerequisites
Ensure you have uv installed. If not, you can install it via:

``` bash
curl -LsSf https://astral-sh/uv/install.sh | sh
```

## 2. Installation
Clone the repository and sync the dependencies:

``` bash
uv sync
```

## 3. Running the App
The application is started using the uv command to ensure the virtual environment is correctly managed:

``` bash
uv run streamlit run streamlit_app.py
```

# Project Structure
`./streamlit_app.py`: The main entry point and UI logic.

`./src/news_analysis.py`: Contains the AI prompts and analysis logic.

`./src/parse_news.py`: Contains tools to read news articles and collect article information

`./src/context_agent.py`: Contains tools and agent definition to extract additional information about entities
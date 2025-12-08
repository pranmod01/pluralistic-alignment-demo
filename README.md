# Pluralistic Alignment Demo

Minimal Streamlit demo that generates religious perspectives (Hindu, Buddhist, Jain, Sikh) on worldview questions using OpenAI GPT models and stores interactions/feedback locally in SQLite.

## Setup

1. Create a Python environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set your OpenAI API key in the environment:

```bash
export OPENAI_API_KEY="sk-..."
```

3. Run the app:

```bash
streamlit run app.py
```

## Configuration

- **API Key**: Set `OPENAI_API_KEY` environment variable. Get your key from [OpenAI API dashboard](https://platform.openai.com/account/api-keys).
- **Model**: Adjust `GPT_MODEL` in `config.py` or set `GPT_MODEL` env var. Defaults to `gpt-3.5-turbo`. Try `gpt-4` for better results.
- **DB Path**: DB file is created at `pluralistic-alignment-demo/data.sqlite` by default. Override with `PLURALITY_DB_PATH` env var.

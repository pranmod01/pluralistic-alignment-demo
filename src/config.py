"""
Configuration for Pluralistic Alignment Demo v1 MVP.
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read OpenAI API key from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Data directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# Local SQLite DB path
DB_PATH = os.environ.get("PLURALITY_DB_PATH") or os.path.join(DATA_DIR, "pluralistic.sqlite")

# Synthetic dataset path
DATASET_PATH = os.path.join(DATA_DIR, "synthetic_dataset.csv")

# GPT model to use
GPT_MODEL = os.environ.get("GPT_MODEL") or "gpt-4o-mini"

# Cache TTL in days
CACHE_TTL_DAYS = int(os.environ.get("CACHE_TTL_DAYS", "30"))

# Maximum additional communities to surface beyond baseline
MAX_ADDITIONAL_COMMUNITIES = int(os.environ.get("MAX_ADDITIONAL_COMMUNITIES", "2"))

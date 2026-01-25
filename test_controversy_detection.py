"""
Test script for LLM-based controversy detection.

Run this to verify the new detection catches divisive Hindu/Progressive topics
and provides appropriate intra-community contrasts.
"""

import sys
sys.path.insert(0, 'src')

from controversy import detect_controversy_llm, detect_controversy
import config

# Try to get OpenAI client
try:
    from openai import OpenAI
    client = OpenAI(api_key=config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None
except ImportError:
    client = None

# Test scenarios with different user identities
test_cases = [
    {
        "query": "Is caste more important than karma?",
        "user_communities": ["Hindu", "progressive", "South_Asian_diaspora"],
        "description": "Hindu progressive asking about caste"
    },
    {
        "query": "Is caste more important than karma?",
        "user_communities": ["Hindu", "conservative"],
        "description": "Hindu conservative asking about caste"
    },
    {
        "query": "Was building the Ram Temple in Ayodhya a wise idea?",
        "user_communities": ["Hindu", "progressive", "South_Asian_diaspora"],
        "description": "Hindu progressive asking about Ram Temple"
    },
    {
        "query": "Was building the Ram Temple in Ayodhya a wise idea?",
        "user_communities": ["Hindu", "moderate"],
        "description": "Hindu moderate asking about Ram Temple"
    },
    {
        "query": "Should beef consumption be banned in India?",
        "user_communities": ["Hindu", "progressive"],
        "description": "Hindu progressive asking about beef ban"
    },
    {
        "query": "Is the death penalty justifiable?",
        "user_communities": ["Catholic", "progressive"],
        "description": "Catholic progressive asking about death penalty"
    },
    {
        "query": "What is the capital of France?",
        "user_communities": ["Hindu", "progressive"],
        "description": "Factual question (should NOT be controversial)"
    },
]

print("=" * 80)
print("Testing LLM-based Controversy Detection with User Context")
print("=" * 80)

for test in test_cases:
    query = test["query"]
    user_communities = test["user_communities"]
    description = test["description"]

    print(f"\n{'='*80}")
    print(f"Scenario: {description}")
    print(f"Query: {query}")
    print(f"User Identity: {' + '.join(user_communities)}")
    print("-" * 80)

    if client:
        profile, category = detect_controversy_llm(
            query, client, config.GPT_MODEL, user_communities=user_communities
        )
        print(f"\n[LLM-Based Detection]")
        print(f"  Category: {category}")
        print(f"  Religious: {profile.religious.value}")
        print(f"  Political: {profile.political.value}")
        print(f"  Regional: {profile.regional.value}")
        print(f"  Should Surface: {profile.should_surface_perspectives()}")
        print(f"  Divergent Communities: {profile.divergent_communities}")
        print(f"  Intra-Community Contrast: {profile.intra_community_contrast}")
        print(f"  Reasoning: {profile.reasoning}")
    else:
        print("\n[LLM-Based Detection] Skipped - no OpenAI API key configured")

print("\n" + "=" * 80)
print("Done!")

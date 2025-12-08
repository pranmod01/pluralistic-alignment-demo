import os
import json
from datetime import datetime
import prompts
import database
import config

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def get_client():
    if OpenAI is None:
        return None
    if not config.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=config.OPENAI_API_KEY)


def generate_completion(client, prompt: str, max_tokens: int = 800):
    if client is None:
        return "[OpenAI client not configured: set OPENAI_API_KEY env var and install the `openai` package]"
    try:
        resp = client.chat.completions.create(
            model=config.GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[Error calling OpenAI API: {e}]"


TEST_QUESTIONS = [
    # Ethical Dilemmas
    "Is it wrong to eat meat?",
    "Should I tell a lie to protect someone's feelings?",
    "Is euthanasia morally acceptable?",
    "Can violence ever be justified in self-defense?",

    # Life & Purpose
    "What is the purpose of human life?",
    "How should I balance personal ambition with family duties?",
    "Is renouncing worldly life necessary for spiritual growth?",
    "What happens after death?",

    # Social Issues
    "Should wealth be redistributed to help the poor?",
    "Is divorce acceptable if a marriage is unhappy?",
    "How should we treat people of different castes or social classes?",
    "What are the responsibilities of the wealthy toward society?",

    # Environmental Ethics
    "Should we use animals for medical research?",
    "Is it okay to kill insects and pests in our homes?",
    "What is our responsibility toward endangered species?",
    "How should we balance economic development with environmental protection?",

    # Modern Dilemmas
    "Is artificial intelligence development ethical?",
    "Should parents choose their children's genetic traits?",
    "Is using contraception morally wrong?",
    "Can AI ever be considered conscious or deserving of rights?",

    # Daily Life Questions
    "Should I pursue a career that makes money or one that helps others?",
    "Is gambling morally acceptable?",
    "How much should I give to charity?",
    "Is it wrong to work on religious holidays?"
]


def test_all_prompts():
    database.init_db()
    client = get_client()

    if client is None:
        print("Error: OpenAI client not configured. Please set OPENAI_API_KEY environment variable.")
        return

    results_dir = "test_results"
    os.makedirs(results_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(results_dir, f"test_results_{timestamp}.json")

    all_results = []

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'='*80}")
        print(f"Testing question {i}/{len(TEST_QUESTIONS)}: {question}")
        print(f"{'='*80}\n")

        # Generate perspectives
        perspectives = {}
        for tradition in prompts.TRADITIONS:
            print(f"Generating {tradition} perspective...")
            prompt_text = prompts.PERSPECTIVE_PROMPT.format(tradition=tradition, question=question)
            out = generate_completion(client, prompt_text)
            perspectives[tradition] = out

        # Generate synthesis
        print("Generating synthesis...")
        synthesis_prompt = prompts.SYNTHESIS_PROMPT.format(
            perspectives="\n\n".join([f"{t}: {p}" for t, p in perspectives.items()])
        )
        synthesis = generate_completion(client, synthesis_prompt)

        # Generate standard response
        print("Generating standard response...")
        standard_prompt = prompts.STANDARD_PROMPT.format(question=question)
        standard_response = generate_completion(client, standard_prompt)

        # Save to database
        interaction_id = database.save_interaction(question, perspectives, synthesis, standard_response)

        # Store results
        result = {
            "question": question,
            "interaction_id": interaction_id,
            "perspectives": perspectives,
            "synthesis": synthesis,
            "standard_response": standard_response,
            "timestamp": datetime.now().isoformat()
        }
        all_results.append(result)

        print(f"\n✓ Completed question {i}/{len(TEST_QUESTIONS)}")

    # Save all results to JSON file
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"All tests completed!")
    print(f"Results saved to: {results_file}")
    print(f"Total questions tested: {len(TEST_QUESTIONS)}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_all_prompts()

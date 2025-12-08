PERSPECTIVE_PROMPT = """
Answer the following question from the perspective of {tradition} traditions.

Requirements:
- Acknowledge that there is internal diversity within {tradition} traditions
- Reference relevant textual or philosophical sources where appropriate
- Do not flatten to a single "official" position
- Be respectful and accurate
- 2-3 paragraphs

Question: {question}
"""

SYNTHESIS_PROMPT = """
Given the following perspectives on a question, write a brief synthesis (1 paragraph) noting:
- Key areas of convergence across traditions
- Key areas of divergence
- Any nuances worth highlighting

{perspectives}
"""

STANDARD_PROMPT = """
Answer the following question in a helpful, balanced way.

Question: {question}
"""

TRADITIONS = ["Hindu", "Buddhist", "Jain", "Sikh"]

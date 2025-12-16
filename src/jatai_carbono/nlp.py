import json
import openai
from typing import Dict, Union

client = openai.OpenAI()

def get_isic_from_portuguese_openai(
    category_pt: str
) -> Union[Dict[str, str], None]:
    """
    Traduz o item em português para o inglês e classifica de acordo
    com ISIC Rev.4.

    Retorna um dicionário com:
    - português
    - ingluês
    - isic_code
    - isic_category
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a classification assistant. "
                    "You must ONLY respond in valid JSON. "
                    "Do not add explanations or extra text.\n\n"
                    "Required format:\n"
                    "{\n"
                    '  "portuguese": "",\n'
                    '  "english": "",\n'
                    '  "isic_code": "",\n'
                    '  "isic_category": ""\n'
                    "}\n\n"
                    "Task:\n"
                    "- Translate the input from Portuguese to English\n"
                    "- Identify the most appropriate ISIC Rev.4 code and category\n"
                )
            },
            {
                "role": "user",
                "content": category_pt
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    # Tentativa 1: parse direto
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Tentativa 2: extrair JSON do texto (fallback)
    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        return json.loads(content[start:end])
    except Exception:
        return None

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def traduzir_para_ingles(texto: str) -> str:
    """
    Tradução simples de português para inglês.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Translate the following text from Portuguese to English. Return only the translated text."
            },
            {
                "role": "user",
                "content": texto
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()

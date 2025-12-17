import json
import re
from typing import Optional
from unidecode import unidecode
import openai

client = openai.OpenAI()

# ------------------------------------------------------------------
# PROMPT SEMÂNTICO (NÍVEL 2)
# ------------------------------------------------------------------

SYSTEM_PROMPT = """
Você é um especialista em inventários de carbono e fatores de emissão.

Sua tarefa NÃO é traduzir textos.
Sua tarefa é identificar o material ou processo produtivo principal
e gerar um termo curto, genérico e adequado para busca de fatores
de emissão na base Climatiq.

Ignore completamente:
- códigos técnicos (ex: CM-30, CAP 50/70)
- normas, especificações e identificadores administrativos
- detalhes locais irrelevantes ambientalmente

Prefira termos amplos e internacionalmente reconhecidos.
"""

USER_PROMPT_TEMPLATE = """
Texto:
"{texto}"

Retorne APENAS um JSON válido no formato:

{{
  "query_climatiq": "<termo curto em inglês para busca no Climatiq>"
}}
"""

# ------------------------------------------------------------------
# FALLBACK HEURÍSTICO (mantido)
# ------------------------------------------------------------------

def extrair_termo_base(texto: str) -> str:
    """
    Fallback simples caso o LLM falhe.
    Remove ruído técnico e mantém núcleo semântico básico.
    """
    if not texto:
        return ""

    texto = unidecode(texto.lower())
    texto = re.sub(r"[^a-z\s]", " ", texto)

    stopwords = {
        "identificacao", "codigo", "tipo", "classe", "norma",
        "cm", "cap", "material", "materia", "prima",
        "servico", "fornecimento"
    }

    tokens = [
        t for t in texto.split()
        if t not in stopwords and len(t) > 2
    ]

    return " ".join(tokens)

# ------------------------------------------------------------------
# FUNÇÃO PRINCIPAL (USADA PELO services.py)
# ------------------------------------------------------------------

def inferir_termo_emissao(texto: str) -> str:
    """
    Gera o termo de busca para o Climatiq usando inferência semântica.
    """

    if not texto:
        return ""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": USER_PROMPT_TEMPLATE.format(texto=texto),
                },
            ],
        )

        content = response.choices[0].message.content.strip()
        data = json.loads(content)

        termo = data.get("query_climatiq")
        if termo:
            return termo

    except Exception:
        pass

    # ---- fallback ----
    termo_base = extrair_termo_base(texto)
    if termo_base:
        return f"{termo_base} production"

    return ""

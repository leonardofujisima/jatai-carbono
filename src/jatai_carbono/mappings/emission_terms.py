EMISSION_TERM_MAP = {
    "gasolina": "gasoline",
    "diesel": "diesel",
    "etanol": "ethanol",
    "alcool": "ethanol",
    "energia eletrica": "electricity",
    "energia": "electricity",
    "gas natural": "natural gas",
    "cimento": "cement",
    "concreto": "concrete",
    "aco": "steel",
    "transporte": "transport",
    "notebook": "computer",
    "computador": "computer"
}


def mapear_termo_emissao(termo_base: str) -> str:
    termo_base = termo_base.lower()

    for chave, termo in EMISSION_TERM_MAP.items():
        if chave in termo_base:
            return termo

    return termo_base

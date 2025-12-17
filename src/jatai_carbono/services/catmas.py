import pandas as pd
from pathlib import Path


COLUNAS_BUSCA = [
    "catmas_material_norm",
    "catmas_material",
    "catmas_classe",
    "catmas_grupo"
]


def buscar_catmas(texto: str) -> pd.DataFrame:
    """
    Busca itens compatíveis na base CATMAS a partir de texto livre.
    Prioriza colunas textuais relevantes do schema CATMAS.
    """

    caminho_parquet = Path("data/catmas/gold/catmas_mg_analitico.parquet")

    if not caminho_parquet.exists():
        raise FileNotFoundError("Arquivo data/catmas.parquet não encontrado.")

    df = pd.read_parquet(caminho_parquet)

    texto = texto.lower().strip()

    colunas_existentes = [c for c in COLUNAS_BUSCA if c in df.columns]

    if not colunas_existentes:
        raise ValueError("Nenhuma coluna textual válida encontrada no CATMAS.")

    mask = False
    for col in colunas_existentes:
        mask |= (
            df[col]
            .astype(str)
            .str.lower()
            .str.contains(texto, na=False)
        )

    return df[mask].head(20)

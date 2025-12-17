from rapidfuzz import process
from typing import Optional
import pandas as pd


def buscar_item_catmas(
    texto_usuario: str,
    df_catmas: pd.DataFrame,
    score_min: int = 85
) -> Optional[pd.Series]:

    texto_norm = texto_usuario.lower()

    resultado = process.extractOne(
        texto_norm,
        df_catmas["catmas_item_norm"],
        score_cutoff=score_min
    )

    if resultado is None:
        return None

    _, score, idx = resultado
    return df_catmas.iloc[idx]

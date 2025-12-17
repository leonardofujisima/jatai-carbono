import pandas as pd
from functools import lru_cache
from pathlib import Path

CATMAS_PATH = Path("data/catmas/gold/catmas_mg_analitico.parquet")

@lru_cache(maxsize=1)
def carregar_catmas() -> pd.DataFrame:
    return pd.read_parquet(CATMAS_PATH)

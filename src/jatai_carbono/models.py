from dataclasses import dataclass
from typing import Optional, List


# --------------------------
# NLP / Classificação ISIC -
# --------------------------

@dataclass
class ISICClassification:
    portuguese: str
    english: str
    isic_code: str
    isic_category: str


# ----------
# Climatiq -
# ----------

@dataclass
class EmissionFactor:
    activity_id: str
    name: str
    category: Optional[str]
    region: Optional[str]
    year: Optional[int]
    unit: Optional[str]
    factor: Optional[float]
    source: Optional[str]
    data_version: Optional[str]


# -----------------------------
# Resultado completo do fluxo -
# -----------------------------

@dataclass
class ItemEmissionSearchResult:
    input_item: str
    classification: ISICClassification
    factors: List[EmissionFactor]

    # Metadata da origem
    source: Optional[str] = None               # "CATMAS-MG" | "NLP"
    catmas_codigo_item: Optional[str] = None
    catmas_item: Optional[str] = None

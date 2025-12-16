from jatai_carbono.models import (
    ISICClassification,
    EmissionFactor,
    ItemEmissionSearchResult
)

from jatai_carbono.nlp import get_isic_from_portuguese_openai
from jatai_carbono.climatiq_client import buscar_fatores_climatiq


def buscar_fatores_por_item(item_pt: str) -> ItemEmissionSearchResult:
    isic_raw = get_isic_from_portuguese_openai(item_pt)

    classification = ISICClassification(**isic_raw)

    fatores_raw = buscar_fatores_climatiq(classification.english)
    fatores = [EmissionFactor(**f) for f in fatores_raw]

    return ItemEmissionSearchResult(
        input_item=item_pt,
        classification=classification,
        factors=fatores
    )

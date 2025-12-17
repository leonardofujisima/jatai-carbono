from jatai_carbono.models import (
    ISICClassification,
    EmissionFactor,
    ItemEmissionSearchResult
)

from jatai_carbono.nlp import get_isic_from_portuguese_openai
from jatai_carbono.climatiq_client import buscar_fatores_climatiq

from jatai_carbono.catmas.loader import carregar_catmas
from jatai_carbono.catmas.search import buscar_item_catmas


def buscar_fatores_por_item(item_pt: str) -> ItemEmissionSearchResult:
    df_catmas = carregar_catmas()
    catmas_match = buscar_item_catmas(item_pt, df_catmas)

    # -------------------------
    # Origem CATMAS
    # -------------------------
    if catmas_match is not None:
        texto_base = catmas_match["catmas_item"]
        source = "CATMAS-MG"
        catmas_codigo_item = catmas_match["catmas_codigo_item"]
        catmas_item = catmas_match["catmas_item"]

    # -------------------------
    # Fallback NLP
    # -------------------------
    else:
        texto_base = item_pt
        source = "NLP"
        catmas_codigo_item = None
        catmas_item = None

    isic_raw = get_isic_from_portuguese_openai(texto_base)
    classification = ISICClassification(**isic_raw)

    fatores_raw = buscar_fatores_climatiq(classification.english)
    fatores = [EmissionFactor(**f) for f in fatores_raw]

    return ItemEmissionSearchResult(
        input_item=item_pt,
        classification=classification,
        factors=fatores,
        source=source,
        catmas_codigo_item=catmas_codigo_item,
        catmas_item=catmas_item
    )


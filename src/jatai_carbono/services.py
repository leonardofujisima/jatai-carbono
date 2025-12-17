from jatai_carbono.catmas.loader import carregar_catmas
from jatai_carbono.catmas.search import buscar_itens_catmas
from jatai_carbono.nlp import get_isic_from_portuguese_openai
from jatai_carbono.climatiq_client import buscar_fatores_climatiq
from jatai_carbono.models import (
    ISICClassification,
    EmissionFactor,
    ItemEmissionSearchResult
)
from jatai_carbono.utils.semantic import extrair_termo_base
from jatai_carbono.mappings.emission_terms import mapear_termo_emissao





def buscar_candidatos_catmas(item_pt: str):
    df_catmas = carregar_catmas()
    return buscar_itens_catmas(item_pt, df_catmas)


def buscar_fatores_por_item(
    item_pt: str,
    catmas_escolhido: dict | None = None
) -> ItemEmissionSearchResult:

    if catmas_escolhido:
        texto_base = catmas_escolhido["catmas_item"]
        source = "CATMAS-MG"
        catmas_codigo_item = catmas_escolhido["catmas_codigo_item"]
        catmas_item = catmas_escolhido["catmas_item"]
    else:
        texto_base = item_pt
        source = "NLP"
        catmas_codigo_item = None
        catmas_item = None

    # ISIC
    isic_raw = get_isic_from_portuguese_openai(texto_base)
    classification = ISICClassification(**isic_raw)

    # Emissões
    termo_base = extrair_termo_base(texto_base)
    termo_emissao = mapear_termo_emissao(termo_base)

    fatores_raw = buscar_fatores_climatiq(termo_emissao)
    fatores = [EmissionFactor(**f) for f in fatores_raw]

    return ItemEmissionSearchResult(
        input_item=item_pt,
        classification=classification,
        factors=fatores,
        source=source,
        catmas_codigo_item=catmas_codigo_item,
        catmas_item=catmas_item
    )


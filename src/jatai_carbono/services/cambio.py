import requests
from datetime import date


FRANKFURTER_API_URL = "https://api.frankfurter.app"


def buscar_taxa_cambio(
    moeda_origem: str,
    moeda_destino: str,
    data_referencia: date | None = None
) -> float:
    """
    Busca taxa de câmbio usando Frankfurter API.

    Retorna:
        1 moeda_origem = X moeda_destino
    """

    moeda_origem = moeda_origem.upper()
    moeda_destino = moeda_destino.upper()

    if data_referencia:
        url = f"{FRANKFURTER_API_URL}/{data_referencia.isoformat()}"
    else:
        url = f"{FRANKFURTER_API_URL}/latest"

    params = {
        "from": moeda_origem,
        "to": moeda_destino
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    rates = data.get("rates", {})
    taxa = rates.get(moeda_destino)

    if taxa is None:
        raise ValueError(
            f"Não foi possível obter taxa de câmbio "
            f"{moeda_origem} → {moeda_destino}"
        )

    return float(taxa)

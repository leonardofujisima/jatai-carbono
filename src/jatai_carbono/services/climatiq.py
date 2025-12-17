import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")


def buscar_fatores_climatiq(query_en: str, limit: int = 10) -> list:
    """
    Busca fatores de emissão na API Climatiq usando texto em inglês.
    """

    if not CLIMATIQ_API_KEY:
        raise EnvironmentError("CLIMATIQ_API_KEY não configurada.")

    url = "https://api.climatiq.io/data/v1/search"

    headers = {
        "Authorization": f"Bearer {CLIMATIQ_API_KEY}"
    }

    params = {
        "query": query_en,
        "data_version": "^3"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json().get("results", [])

import re
import unicodedata


def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def extrair_termo_base(texto: str) -> str:
    """
    Extrai o núcleo semântico do texto para uso em fatores de emissão.
    """
    texto = normalizar_texto(texto)

    stopwords = {
        "tipo", "comum", "padrao", "servico", "execucao", "fornecimento",
        "instalacao", "sistema", "equipamento", "material", "produto",
        "automotiva", "automotivo", "em", "para", "de", "do", "da"
    }

    tokens = [t for t in texto.split() if t not in stopwords]

    # Retorna até 3 termos relevantes
    return " ".join(tokens[:3])

from rapidfuzz import process
import pandas as pd

PALAVRAS_SERVICO = {
    "manutencao", "execucao", "instalacao", "servico",
    "conserto", "reparo", "assistencia"
}


def buscar_itens_catmas(
    texto_usuario: str,
    df_catmas: pd.DataFrame,
    score_min: int = 80,
    top_n: int = 5
) -> pd.DataFrame | None:

    texto_usuario = texto_usuario.lower().strip()
    tokens_usuario = texto_usuario.split()

    resultados = process.extract(
        texto_usuario,
        df_catmas["catmas_item_norm"],
        score_cutoff=score_min,
        limit=top_n
    )

    if not resultados:
        return None

    candidatos = df_catmas.iloc[[r[2] for r in resultados]].copy()
    candidatos["score"] = [r[1] for r in resultados]

    # Penaliza serviços se input for genérico
    if len(tokens_usuario) == 1:
        candidatos["penal_servico"] = candidatos["catmas_item_norm"].apply(
            lambda x: any(p in x for p in PALAVRAS_SERVICO)
        )
        candidatos.loc[candidatos["penal_servico"], "score"] -= 10

    # Prioriza materiais
    candidatos["is_material"] = candidatos["tipo_material_servico"].str.contains(
        "material", case=False, na=False
    )
    candidatos.loc[candidatos["is_material"], "score"] += 5

    candidatos = candidatos.sort_values("score", ascending=False)

    return candidatos


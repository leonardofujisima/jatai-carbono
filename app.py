import sys
from pathlib import Path
SRC_PATH = Path(__file__).resolve().parent / "src"
sys.path.append(str(SRC_PATH))

import streamlit as st
from jatai_carbono.services import (
    buscar_candidatos_catmas,
    buscar_fatores_por_item
)

st.set_page_config(page_title="Jataí Carbono", page_icon="🌱", layout="centered")

st.title("🌱 Jataí Carbono")
st.caption("Estimativa de emissões com base em CATMAS-MG e Climatiq")

item = st.text_input("Descreva o item ou serviço")

if item:
    candidatos = buscar_candidatos_catmas(item)

    # -----------------------------
    # CASO 1: CATMAS encontrou opções
    # -----------------------------
    if candidatos is not None and len(candidatos) > 1:
        st.info("Encontramos mais de um item no CATMAS. Selecione o mais adequado:")

        opcoes = {
            f"{row.catmas_item} (Código {row.catmas_codigo_item})": row.to_dict()
            for _, row in candidatos.iterrows()
        }

        escolha = st.radio(
            "Escolha o item CATMAS:",
            options=list(opcoes.keys())
        )

        if st.button("Confirmar item"):
            resultado = buscar_fatores_por_item(
                item,
                catmas_escolhido=opcoes[escolha]
            )
        else:
            resultado = None

    # -----------------------------
    # CASO 2: CATMAS encontrou 1 item
    # -----------------------------
    elif candidatos is not None and len(candidatos) == 1:
        row = candidatos.iloc[0]
        resultado = buscar_fatores_por_item(
            item,
            catmas_escolhido=row.to_dict()
        )
        st.success("Item identificado automaticamente no CATMAS-MG.")

    # -----------------------------
    # CASO 3: Não achou no CATMAS
    # -----------------------------
    else:
        st.warning("Item não identificado no CATMAS. Classificação automática aplicada.")
        resultado = buscar_fatores_por_item(item)

    # -----------------------------
    # MOSTRAR RESULTADO
    # -----------------------------
    if resultado:
        if resultado.source == "CATMAS-MG":
            with st.expander("Detalhes do item CATMAS"):
                st.markdown(f"""
                **Código CATMAS:** {resultado.catmas_codigo_item}  
                **Descrição:** {resultado.catmas_item}
                """)

        st.subheader("Classificação ISIC")
        st.markdown(f"""
        **Português:** {resultado.classification.portuguese}  
        **Inglês:** {resultado.classification.english}  
        **Código ISIC:** {resultado.classification.isic_code}  
        **Categoria:** {resultado.classification.isic_category}
        """)

        st.subheader("Fatores de emissão (Climatiq)")
        if resultado.factors:
            for f in resultado.factors:
                st.markdown(f"""
                **{f.name}**  
                Fator: `{f.factor} {f.unit}`  
                Fonte: {f.source}
                """)
                st.divider()
        else:
            st.warning("Nenhum fator de emissão encontrado.")

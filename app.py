import sys
from pathlib import Path

# Adiciona src/ ao PYTHONPATH
SRC_PATH = Path(__file__).resolve().parent / "src"
sys.path.append(str(SRC_PATH))

import streamlit as st
from jatai_carbono.services import buscar_fatores_por_item

st.set_page_config(page_title="Jataí Carbono", layout="centered")

st.title("🌱 Jataí Carbono")
st.caption("Estimativa de emissões com base em CATMAS-MG e Climatiq")

item = st.text_input("Descreva o item ou serviço")

if item:
    with st.spinner("Processando..."):
        resultado = buscar_fatores_por_item(item)

    # -------------------------
    # Origem do item
    # -------------------------
    if resultado.source == "CATMAS-MG":
        st.success("✅ Item identificado no CATMAS – Governo de Minas Gerais")

        with st.expander("Ver detalhes do item CATMAS"):
            st.markdown(f"""
            **Código CATMAS:** {resultado.catmas_codigo_item}  
            **Descrição oficial:** {resultado.catmas_item}
            """)
    else:
        st.info("ℹ️ Item não identificado no CATMAS. Classificação automática aplicada.")

    # -------------------------
    # Classificação ISIC
    # -------------------------
    st.subheader("Classificação ISIC")
    st.markdown(f"""
    **Português:** {resultado.classification.portuguese}  
    **Inglês:** {resultado.classification.english}  
    **Código ISIC:** {resultado.classification.isic_code}  
    **Categoria:** {resultado.classification.isic_category}
    """)

    # -------------------------
    # Fatores de emissão
    # -------------------------
    st.subheader("Fatores de emissão (Climatiq)")

    if resultado.factors:
        for f in resultado.factors:
            st.markdown(f"""
            **{f.name}**  
            Região: {f.region} | Ano: {f.year}  
            Fator: `{f.factor} {f.unit}`  
            Fonte: {f.source}
            """)
            st.divider()
    else:
        st.warning("Nenhum fator de emissão encontrado.")


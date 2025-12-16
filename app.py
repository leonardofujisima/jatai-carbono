import streamlit as st

from jatai_carbono import buscar_fatores_por_item
from jatai_carbono.models import EmissionFactor


# ---------------------------
# Configuração da página
# ---------------------------

st.set_page_config(
    page_title="Jataí Carbono",
    page_icon="🌱",
    layout="centered"
)

st.title("🌱 Jataí Carbono")
st.caption(
    "Estimativa de fatores de emissão para itens de compras públicas, "
    "com base em classificação internacional e dados Climatiq."
)

st.divider()


# ---------------------------
# Entrada do usuário
# ---------------------------

item_pt = st.text_input(
    label="Descreva o item da compra pública",
    placeholder="Ex: Asfalto usinado a quente, Diesel S10, Energia elétrica..."
)


# ---------------------------
# Ação principal
# ---------------------------

if st.button("Buscar fatores de emissão", type="primary"):

    if not item_pt.strip():
        st.warning("Por favor, informe um item para pesquisa.")
        st.stop()

    with st.spinner("Classificando item e consultando base de fatores..."):
        try:
            resultado = buscar_fatores_por_item(item_pt)
        except Exception as e:
            st.error(f"Erro ao processar o item: {e}")
            st.stop()

    # ---------------------------
    # Resultado NLP
    # ---------------------------

    st.subheader("🔎 Classificação do item")

    st.markdown(
        f"""
        **Descrição original:** {resultado.input_item}  
        **Tradução (inglês):** {resultado.classification.english}  
        **ISIC:** {resultado.classification.isic_code} — {resultado.classification.isic_category}
        """
    )

    # ---------------------------
    # Resultados Climatiq
    # ---------------------------

    st.subheader("📊 Fatores de emissão encontrados")

    if not resultado.factors:
        st.info("Nenhum fator de emissão encontrado para este item.")
        st.stop()

    # Converter para tabela simples (Streamlit aceita list[dict])
    tabela = [
        {
            "Atividade": f.name,
            "Categoria": f.category,
            "Região": f.region,
            "Ano": f.year,
            "Unidade": f.unit,
            "Fator": f.factor,
            "Fonte": f.source,
        }
        for f in resultado.factors
    ]

    st.dataframe(tabela, use_container_width=True)

    st.caption(
        "Fonte dos dados: Climatiq. Classificação ISIC utilizada para apoio à busca."
    )

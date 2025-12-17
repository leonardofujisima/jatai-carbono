import sys
from pathlib import Path

# Garante que src/ esteja no PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent / "src"))

import html as html_lib
import streamlit as st
import streamlit.components.v1 as components

from jatai_carbono.services.catmas import buscar_catmas
from jatai_carbono.services.translate import traduzir_para_ingles
from jatai_carbono.services.climatiq import buscar_fatores_climatiq


def formatar_decimal_ptbr(valor: float) -> str:
    """
    Formata número decimal no padrão pt-BR,
    arredondando para duas casas decimais.
    """
    return f"{valor:.2f}".replace(".", ",")


# ============================================================
# Configuração da página
# ============================================================
st.set_page_config(
    page_title="Instituto Jataí | Busca de fatores de emissão",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# Header
# ============================================================
st.markdown(
"""
<div style="padding: 1.5rem 0;">
  <h1 style="color:#2F6B4F; font-weight:700; margin-bottom:0.3rem;">
    Instituto Jataí — Busca de fatores de emissão
  </h1>
  <p style="font-size:1.05rem; max-width:720px; margin-top:0;">
    Ferramenta experimental para apoiar a identificação de fatores de emissão
    a partir de descrições textuais de itens e insumos.
  </p>
</div>
""",
unsafe_allow_html=True
)

# ============================================================
# Input
# ============================================================
st.markdown("### O que você quer buscar?")
texto = st.text_input(
    "",
    placeholder="Ex.: concreto, diesel rodoviário, energia elétrica"
)

if not texto:
    st.stop()

# ============================================================
# CATMAS
# ============================================================
st.markdown("## Base CATMAS")
st.markdown(
    "<p style='color:#4F6F63; margin-top:-0.5rem;'>Itens compatíveis encontrados na base de compras públicas.</p>",
    unsafe_allow_html=True
)

try:
    df_catmas = buscar_catmas(texto)
    if df_catmas.empty:
        st.info("Nenhum material ou serviço encontrado no CATMAS.")
    else:
        st.dataframe(df_catmas, use_container_width=True)
except Exception as e:
    st.error(f"Erro ao buscar CATMAS: {e}")
    st.stop()

# ============================================================
# Tradução
# ============================================================

try:
    texto_en = traduzir_para_ingles(texto)
except Exception as e:
    st.error(f"Erro na tradução: {e}")
    st.stop()

# ============================================================
# Climatiq
# ============================================================
st.markdown("## Fatores de emissão (Climatiq)")

try:
    resultados = buscar_fatores_climatiq(texto_en)

    if not resultados:
        st.warning("Nenhum fator encontrado na Climatiq.")
        st.stop()

    for r in resultados:
        if not isinstance(r, dict):
            continue

        # ----------------------------
        # Campos principais
        # ----------------------------
        name = html_lib.escape(str(r.get("name", "Sem nome")))
        category = html_lib.escape(str(r.get("category", "—")))
        region = html_lib.escape(str(r.get("region", "—")))
        year = html_lib.escape(str(r.get("year", "—")))
        source_dataset = html_lib.escape(str(r.get("source_dataset", "—")))
        source_lca_activity = html_lib.escape(str(r.get("source_lca_activity", "—")))

        # ----------------------------
        # Fator de emissão (robusto)
        # ----------------------------
        factor_value = r.get("factor") or r.get("co2e_factor")
        functional_unit = r.get("unit") or r.get("co2e_unit")

        if factor_value is not None:
            if functional_unit:
                valor_formatado = formatar_decimal_ptbr(float(factor_value))
                factor_display = (
                    f"{valor_formatado} kgCO₂e / {functional_unit.split('/')[-1]}"
                )
            else:
                factor_display = f"{factor_value} kgCO₂e"
        else:
            factor_display = "Fator de emissão não informado"

        factor_display = html_lib.escape(factor_display)

        # ----------------------------
        # Card HTML (renderização real)
        # ----------------------------
        card_html = f"""
<div style="
    border: 1px solid #D9E4DD;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    margin: 0 0 1rem 0;
    background: #FFFFFF;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
">
  <div style="
      font-size: 1.05rem;
      font-weight: 700;
      color: #2F6B4F;
      margin-bottom: 0.25rem;
  ">
    {name}
  </div>

  <div style="
      font-size: 1.25rem;
      font-weight: 700;
      color: #1F4D3A;
      margin-bottom: 0.6rem;
  ">
    {factor_display}
  </div>

  <div style="
      font-size: 0.92rem;
      color: #3E5F54;
      line-height: 1.55;
  ">
    <div><strong>Categoria:</strong> {category}</div>
    <div><strong>Região:</strong> {region}</div>
    <div><strong>Ano:</strong> {year}</div>
    <div><strong>Base de dados:</strong> {source_dataset}</div>
    <div><strong>Atividade do ciclo de vida:</strong> {source_lca_activity}</div>
  </div>
</div>
"""

        components.html(card_html, height=200)

except Exception as e:
    st.error(f"Erro ao consultar Climatiq: {e}")




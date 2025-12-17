import sys
from pathlib import Path

# Garante que src/ esteja no PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent / "src"))

import streamlit as st

from jatai_carbono.services.catmas import buscar_catmas
from jatai_carbono.services.translate import traduzir_para_ingles
from jatai_carbono.services.climatiq import buscar_fatores_climatiq
from jatai_carbono.services.cambio import buscar_taxa_cambio

import re
import unicodedata


# ============================================================
# Utils
# ============================================================

def formatar_decimal_ptbr(valor: float) -> str:
    """Formata número decimal no padrão pt-BR."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparação."""
    if not texto:
        return ""

    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def limpar_unidade(unidade: str) -> str:
    """Remove parênteses, aspas e espaços extras."""
    if not unidade:
        return ""
    unidade = str(unidade)
    unidade = unidade.replace("(", "").replace(")", "")
    unidade = unidade.replace("'", "").replace('"', "")
    return unidade.strip()


# ============================================================
# Configuração da página
# ============================================================

st.set_page_config(
    page_title="Instituto Jataí | Cálculo de Emissões",
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
        Instituto Jataí — Cálculo de emissões de carbono
      </h1>
      <p style="font-size:1.05rem; max-width:760px; margin-top:0;">
        Ferramenta experimental para identificação de fatores de emissão
        e cálculo de emissões de carbono a partir de unidades compatíveis.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# Input principal
# ============================================================

st.markdown("### O que você quer buscar?")
texto = st.text_input(
    "O que você quer buscar?",
    placeholder="Ex.: concreto, diesel rodoviário, energia elétrica",
    label_visibility="collapsed"
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
    df_catmas = buscar_catmas(normalizar_texto(texto))

    if df_catmas.empty:
        st.info("Nenhum material ou serviço encontrado no CATMAS.")
    else:
        st.dataframe(
            df_catmas
            .drop(columns=["catmas_material_norm"], errors="ignore")
            .reset_index(drop=True),
            hide_index=True,
            use_container_width=True
        )

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
# Climatiq — busca, seleção e cálculo
# ============================================================

st.markdown("## Fatores de emissão (Climatiq)")

# Lista completa de moedas possíveis
MOEDAS_CLIMATIQ = {
    "aed","afn","all","amd","ang","aoa","ars","aud","awg","azn","bam","bbd",
    "bdt","bgn","bhd","bif","bmd","bnd","bob","brl","bsd","bwp","byn","cad",
    "chf","clp","cny","cop","crc","cve","czk","djf","dkk","dop","dzd","egp",
    "etb","eur","fjd","gbp","gel","ghs","gip","gmd","gtq","gyd","hkd","hnl",
    "huf","idr","ils","inr","iqd","irr","isk","jmd","jod","jpy","kes","kgs",
    "khr","kmf","krw","kwd","kyd","kzt","lak","lbp","lsl","lyd","mad","mdl",
    "mga","mkd","mop","mur","mvr","mxn","myr","mzn","nad","nio","nok","npr",
    "nzd","omr","pab","pen","php","pkr","pln","pyg","qar","ron","rsd","rub",
    "rwf","sar","scr","sek","sgd","sle","srd","std","szl","thb","tjs","tnd",
    "try","ttd","twd","uah","ugx","usd","uyu","uzs","vnd","wst","xaf","xcd",
    "xof","xpf","yer","zar","zmw"
}

try:
    resultados = buscar_fatores_climatiq(texto_en)

    if not resultados:
        st.warning("Nenhum fator encontrado na Climatiq.")
        st.stop()

    fatores = []

    for r in resultados:
        factor_value = r.get("factor") or r.get("co2e_factor")
        functional_unit = r.get("unit") or r.get("co2e_unit")

        if not factor_value or not functional_unit:
            continue

        nome = r.get("name", "Fator sem nome")
        regiao = r.get("region", "—")
        ano = r.get("year", "—")
        lca = r.get("source_lca_activity", "—")

        unidade_limpa = limpar_unidade(r.get("unit_type", "-"))

        label = f"{nome} — {regiao} — {ano} — {unidade_limpa} — {lca}"

        fatores.append({
            "label": label,
            "name": nome,
            "category": r.get("category"),
            "region": regiao,
            "year": ano,
            "unit_type": unidade_limpa,
            "source_dataset": r.get("source_dataset"),
            "source_lca_activity": lca,
            "factor_value": float(factor_value),
            "functional_unit": limpar_unidade(functional_unit)
        })

    if not fatores:
        st.warning("Nenhum fator com unidade válida para cálculo.")
        st.stop()

    # --------------------------------------------------------
    # Seleção do fator
    # --------------------------------------------------------
    st.markdown("### Selecione o fator de emissão")

    fator_escolhido = st.selectbox(
        "Selecione o fator",
        options=fatores,
        format_func=lambda x: x["label"],
        label_visibility="collapsed"
    )

    # --------------------------------------------------------
    # Metadados do fator
    # --------------------------------------------------------
    st.markdown("#### Detalhes do fator selecionado")

    st.markdown(
        f"""
        - **Fator:** {fator_escolhido["factor_value"]}
        - **Unidade:** {fator_escolhido["functional_unit"]}
        - **Categoria:** {fator_escolhido["category"]}
        - **Região:** {fator_escolhido["region"]}
        - **Ano:** {fator_escolhido["year"]}
        - **Base de dados:** {fator_escolhido["source_dataset"]}
        - **Atividade do ciclo de vida:** {fator_escolhido["source_lca_activity"]}
        """
    )

    # --------------------------------------------------------
    # Input guiado pela unidade
    # --------------------------------------------------------
    functional_unit = fator_escolhido["functional_unit"]
    factor_value = fator_escolhido["factor_value"]

    unidade_atividade = functional_unit.split("/")[-1].strip().lower()
    eh_fator_monetario = unidade_atividade in MOEDAS_CLIMATIQ

    st.markdown("### Informe a atividade")

    if eh_fator_monetario:
        moeda_fator = unidade_atividade.upper()

        valor_brl = st.number_input(
            "Valor da contratação (R$)",
            min_value=0.0,
            step=100.0
        )

        st.caption(
            f"Este fator utiliza a moeda {moeda_fator}. "
            "O valor informado será convertido automaticamente a partir de R$."
        )

        if valor_brl > 0:
            taxa = buscar_taxa_cambio("BRL", moeda_fator)
            valor_convertido = valor_brl * taxa
            emissao_total = valor_convertido * factor_value

            st.markdown("### Resultado")

            st.metric(
                label="Emissões estimadas",
                value=f"{formatar_decimal_ptbr(emissao_total)} kg CO₂e"
            )

            st.caption(
                f"Conversão utilizada: 1 BRL = {taxa:.4f} {moeda_fator}"
            )

    else:
        atividade = st.number_input(
            f"Quantidade ({unidade_atividade})",
            min_value=0.0,
            step=1.0
        )

        if atividade > 0:
            emissao_total = atividade * factor_value

            st.markdown("### Resultado")

            st.metric(
                label="Emissões estimadas",
                value=f"{formatar_decimal_ptbr(emissao_total)} kg CO₂e"
            )

    st.caption(
        "As emissões apresentadas são estimativas baseadas em fatores médios "
        "de emissão da base Climatiq e não substituem inventários oficiais auditados."
    )

except Exception as e:
    st.error(f"Erro ao consultar Climatiq: {e}")

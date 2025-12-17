#=============================
#= Importação de bibliotecas =
#=============================

library(readr)
library(dplyr)
library(stringr)
library(janitor)
library(arrow)
library(digest)

#===================================================
#= Importação de arquivo de compras públicas de MG =
#===================================================

catmas_raw <- read_csv(
  "C:/Users/leona/OneDrive/Desktop/minas-jatai/data/df_catmas_mg.csv",
  locale = locale(encoding = "UTF-8")
)

#=====================================================
#= Limpeza da base de dados e normalização de textos =
#=====================================================

# Limpeza inicial de nomes
catmas <- catmas_raw %>% 
  clean_names() %>% 
  select(
    catmas_codigo_grupo,
    catmas_grupo,
    catmas_codigo_classe,
    catmas_classe,
    catmas_codigo_material,
    catmas_material
  )

# Função para normalização de textos
normalizar_texto <- function(x) {
  x %>%
    str_replace_all("_x000D_", " ") %>%
    str_replace_all("[\r\n]", " ") %>%
    str_to_lower() %>%
    stringi::stri_trans_general("Latin-ASCII") %>%
    str_replace_all("[^a-z0-9 ]", " ") %>%
    str_squish()
}

# Normalização da descrição dos itens
catmas <- catmas %>%
  mutate(
    catmas_material_norm = normalizar_texto(catmas_material)
  )

# Criação de base tratada
catmas_tratado <- catmas %>%
  group_by(
    catmas_codigo_grupo,
    catmas_codigo_classe,
    catmas_codigo_material
  ) %>%
  slice_max(nchar(catmas_material_norm), with_ties = FALSE) 


# Validação de itens duplicados
catmas_tratado %>%
  count() %>%
  filter(n > 1)

#=======================
#= Exportação de dados = 
#=======================

write_parquet(
  catmas_tratado,
  sink = "C:/Users/leona/OneDrive/Desktop/jatai-carbono/data/catmas/gold/catmas_mg_analitico.parquet",
  compression = "snappy"
)



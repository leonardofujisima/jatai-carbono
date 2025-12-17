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
  clean_names()

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
    catmas_item_norm = normalizar_texto(catmas_item)
  )

# Criação de base tratada
catmas_tratado <- catmas %>%
  group_by(
    catmas_codigo_grupo,
    catmas_codigo_classe,
    catmas_codigo_material,
    catmas_codigo_item
  ) %>%
  slice_max(nchar(catmas_item_norm), with_ties = FALSE) %>%
  ungroup()

# Criação da base final e ID de item
catmas_final <- catmas_tratado %>%
  mutate(
    catmas_item_key = paste(
      "MG_CATMAS",
      catmas_codigo_grupo,
      catmas_codigo_classe,
      catmas_codigo_material,
      catmas_codigo_item,
      sep = "_"
    ),
    catmas_item_id = paste0(
      catmas_item_key,
      "_",
      substr(digest::digest(catmas_item_norm), 1, 8)
    )
  )

# Validação de itens duplicados
catmas_final %>%
  count(catmas_item_id) %>%
  filter(n > 1)

#=======================
#= Exportação de dados = 
#=======================

write_parquet(
  catmas_final,
  sink = "C:/Users/leona/OneDrive/Desktop/jatai-carbono/data/catmas/gold/catmas_mg_analitico.parquet",
  compression = "snappy"
)



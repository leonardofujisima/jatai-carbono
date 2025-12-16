# Importação das bibliotecas
import os
from dotenv import load_dotenv

# Importa variáveis ambiente
load_dotenv()

# API da Climatiq
CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")
# API da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


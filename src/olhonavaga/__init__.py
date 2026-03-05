# OlhoNaVaga/__init__.py

from .parser import RankingParser
from .scraper import OlhoNaVaga

# O __all__ define o que será importado ao usar "from OlhoNaVaga import *"
__all__ = ["OlhoNaVaga", "RankingParser"]

__version__ = "1.0.0"

# OlhoNaVaga/
# ├── __init__.py      # Interface simplificada
# ├── browser.py       # Configuração do Selenium/Chrome
# ├── scraper.py       # Lógica de navegação e busca de elementos
# ├── parser.py        # Lógica de extração de texto e limpeza (Pura)
# └── storage.py       # Salvamento em Parquet

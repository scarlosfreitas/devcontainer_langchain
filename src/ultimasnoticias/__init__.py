# OlhoNaVaga/__init__.py

from .parser import BaseParser, NoticiasParser
from .scraper import Noticias

# O __all__ define o que será importado ao usar "from OlhoNaVaga import *"
__all__ = ["Noticias", "BaseParser", "NoticiasParser"]

__version__ = "1.0.0"

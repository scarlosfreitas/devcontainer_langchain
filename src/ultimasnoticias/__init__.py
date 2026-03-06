# ultimasnoticias/__init__.py

from .parser import BaseParser, NoticiasParser
from .scraper import Noticias
from .telegram import Telegram

# O __all__ define o que será importado ao usar "from ultimasnoticias import *"
__all__ = [
    "Noticias",
    "BaseParser",
    "NoticiasParser",
    "Telegram",
]


__version__ = "1.0.0"

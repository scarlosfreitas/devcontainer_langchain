import sys

sys.path.append("/workspace/src/")

from ultimasnoticias.storage import Storage

db = Storage(verbose=True)
print(db.DB_STRING)

db.create(verbose=True)

from ultimasnoticias.scraper import Noticias

nav = Noticias()


print(nav.get_url())
print(nav.get_url(fonte="gran"))
print(nav.get_url(fonte="gran", uf="df"))
print(nav.get_url(fonte="gran", uf="pa"))
print(nav.get_url(fonte="fcc", uf="go"))
print(nav.get_url(fonte="cebraspe", uf="rn"))
print(nav.get_url(fonte="cebraspe_novos"))

print(nav.get_url(verbose=True))
print(nav.get_url(fonte="gran", verbose=True))
print(nav.get_url(fonte="gran", uf="df", verbose=True))
print(nav.get_url(fonte="gran", uf="pa", verbose=True))
print(nav.get_url(fonte="fcc", uf="go", verbose=True))
print(nav.get_url(fonte="cebraspe", uf="rn", verbose=True))
print(nav.get_url(fonte="cebraspe_novos", verbose=True))

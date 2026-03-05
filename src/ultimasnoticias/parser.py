# locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
import datetime as dt
import hashlib
import re

from selenium.webdriver.common.by import By


class BaseParser:
    @staticmethod
    def text_to_date(text_date):
        MONTHS = {
            "janeiro": "January",
            "fevereiro": "February",
            "março": "March",
            "abril": "April",
            "maio": "May",
            "junho": "June",
            "julho": "July",
            "agosto": "August",
            "setembro": "September",
            "outubro": "October",
            "novembro": "November",
            "dezembro": "December",
        }

        # Substitui o mês em português pelo equivalente em inglês
        for pt, en in MONTHS.items():
            if pt in text_date:
                text_date = text_date.replace(pt, en)
                break

        if len(text_date) == 4:
            return dt.datetime.strptime(
                "1 de January de " + text_date, "%d de %B de %Y"
            ).date()
        else:
            return dt.datetime.strptime(text_date, "%d de %B de %Y").date()

    @staticmethod
    def corrige_dois_pontos(texto):
        # texto = "Olá mundo!"
        if texto.find(":") == -1:
            pattern = r"(2022|2023|2024|2025|2026)"
            texto = re.sub(pattern, r"\1:", texto, count=1)

        return texto


class NoticiasParser:
    @staticmethod
    def rec_gran_from_text(texto, uf, url="", verbose=False):
        texto = BaseParser.corrige_dois_pontos(texto)
        registro = {}
        registro["hashid"] = hashlib.sha256(texto.encode()).hexdigest()
        registro["sefaz"] = uf
        registro["dtnoticia"] = BaseParser.text_to_date(texto.split(":")[0])
        registro["dsnoticia"] = BaseParser.text_to_date(texto.split(":")[0])
        registro["txcompleto"] = texto
        registro["url"] = url
        registro["tsatualizacao"] = dt.datetime.now()

        if not verbose:
            print("reg_gran_from_text: ", registro)

        return registro

    @staticmethod
    def rec_fcc_from_text(texto, uf, url="", verbose=False):
        registro = {}
        registro["hashid"] = hashlib.sha256(texto.encode()).hexdigest()
        registro["sefaz"] = uf
        registro["txcompleto"] = texto
        registro["url"] = url
        registro["tsatualizacao"] = dt.datetime.now()

        if not verbose:
            print("reg_fcc_from_text: ", registro)

        return registro

    @staticmethod
    def rec_cebraspe_from_text(texto, uf, url="", verbose=False):
        dtnoticia, dsnoticia = texto.split("\n")

        registro = {}
        registro["hashid"] = hashlib.sha256(texto.encode()).hexdigest()
        registro["sefaz"] = uf
        registro["dtnoticia"] = dt.datetime.strptime(dtnoticia, "%d/%m/%Y %H:%M")
        registro["dsnoticia"] = dsnoticia
        registro["txcompleto"] = texto
        registro["url"] = url
        registro["tsatualizacao"] = dt.datetime.now()

        if not verbose:
            print("rec_cebraspe_from_text: ", registro)

        return registro

    @staticmethod
    def rec_cebraspe_novos_from_text(texto, url="", verbose=False):

        registro = {}
        registro["hashid"] = hashlib.sha256(texto.encode()).hexdigest()
        registro["txcompleto"] = texto
        registro["url"] = url
        registro["tsatualizacao"] = dt.datetime.now()

        if not verbose:
            print("rec_cebraspe_novos_from_text: ", registro)

        return registro

    @staticmethod
    def rec_from_text(texto, uf, fonte="gran", url="", verbose=False):
        if "fcc" in fonte:
            return NoticiasParser.rec_fcc_from_text(texto, uf, url=url, verbose=verbose)
        elif "cebraspe" == fonte:
            return NoticiasParser.rec_cebraspe_from_text(
                texto, uf, url=url, verbose=verbose
            )
        elif "cebraspe_novos" == fonte:
            return NoticiasParser.rec_cebraspe_from_text(
                texto, url=url, verbose=verbose
            )
        else:
            return NoticiasParser.rec_gran_from_text(
                texto, uf, url=url, verbose=verbose
            )

    @staticmethod
    def gran_list_text(driver, verbose=False):
        titulo_situacao = driver.find_elements(By.XPATH, '//h2[@id="situacao"]')
        ul_posterior = titulo_situacao[0].find_elements(
            By.XPATH, "following-sibling::ul"
        )
        lista_li = ul_posterior[0].find_elements(By.XPATH, "./li")
        lista_texto = [elemento.text for elemento in lista_li]

        if not verbose:
            print("gran_list_text: ", lista_texto)

        return lista_texto

    @staticmethod
    def fcc_linkarquivo_list_text(driver, verbose=False):
        div_link_arquivo = driver.find_elements(By.XPATH, '//div[@class="linkArquivo"]')
        lista_div_item = div_link_arquivo[0].find_elements(By.XPATH, "./div")
        lista_texto = [elemento.text for elemento in lista_div_item]

        if not verbose:
            print("fcc_linkarquivo_list_text: ", lista_texto)

        return lista_texto

    @staticmethod
    def fcc_publicacao_list_text(driver, verbose=False):
        div_publicacao = driver.find_elements(
            By.XPATH, '//div[@class="rotuloTopico1"][contains(., "Publicações")]'
        )
        if len(div_publicacao) > 0:
            div_posterior = div_publicacao[0].find_elements(
                By.XPATH, "following-sibling::div"
            )
            lista_publicacao = div_posterior[0].text.split("\n")
            lista_texto = [
                pub.lstrip("- ").strip() for pub in lista_publicacao if pub != ""
            ]
        else:
            lista_texto = []

        if not verbose:
            print("fcc_publicacao_list_text: ", lista_texto)

        return lista_texto

    @staticmethod
    def cebraspe_list_text(driver, verbose=False):
        lista_titulo = [
            "Acesso a links",
            "Editais, comunicados e informações",
            "Provas e gabaritos",
        ]
        lista_texto = []
        for titulo in lista_titulo:
            div_acesso_a_links = driver.find_elements(
                By.XPATH, '//h2[contains(., "{}")]/ancestor::div[3]'.format(titulo)
            )
            if len(div_acesso_a_links) > 0:
                lista_li_links = div_acesso_a_links[0].find_elements(By.XPATH, ".//li")
                lista_texto = lista_texto + [li.text for li in lista_li_links]
                # lista_texto

        if not verbose:
            print("cebraspe_list_text: ", lista_texto)

        return lista_texto

    @staticmethod
    def cebraspe_novos_list_text(driver, verbose=False):
        lista_texto = []

        div_novos_concursos = driver.find_elements(
            By.XPATH, '//h1[contains(., "Novos")]/ancestor::div[3]'
        )
        if len(div_novos_concursos) > 0:
            lista_li_cards = div_novos_concursos[0].find_elements(By.XPATH, ".//li")
            lista_texto = lista_texto + [
                li.text.replace("\nMAIS INFORMAÇÕES", "").replace("\n", " - ")
                for li in lista_li_cards
            ]
            # lista_texto

        if not verbose:
            print("cebraspe_novos_list_text: ", lista_texto)

        return lista_texto

    @staticmethod
    def list_text(driver, fonte="gran", verbose=False):
        if fonte == "fcc_linkarquivo":
            return NoticiasParser.fcc_linkarquivo_list_text(driver, verbose=verbose)
        elif fonte == "fcc_publicacao":
            return NoticiasParser.fcc_publicacao_list_text(driver, verbose=verbose)
        elif fonte == "cebraspe_novos":
            return NoticiasParser.cebraspe_novos_list_text(driver, verbose=verbose)
        elif fonte == "cebraspe":
            return NoticiasParser.cebraspe_list_text(driver, verbose=verbose)
        else:
            return NoticiasParser.gran_list_text(driver, verbose=verbose)

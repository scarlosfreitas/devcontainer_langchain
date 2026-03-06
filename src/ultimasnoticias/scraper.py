import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .browser import get_uc_driver
from .parser import NoticiasParser as np
from .storage import Storage


class Noticias:
    FCC_URL = {
        "go": "https://www.concursosfcc.com.br/concursos/seego125/index.html",
        "pi": "https://www.concursosfcc.com.br/concursos/sefpi124/index.html",
        "sp": "https://www.concursosfcc.com.br/concursos/fazsp125/index.html",
        "mt": "https://www.concursosfcc.com.br/concursos/sefmt125/index.html",
        # 'ce':{'url': 'https://www.concursosfcc.com.br/concursos//index.html',},
    }

    CEBRASPE_URL = {
        "rj": "https://www.cebraspe.org.br/concursos/SEFAZ_RJ_25_AUDITOR",
        "se": "https://www.cebraspe.org.br/concursos/SEFAZ_SE_25_AUDITOR",
        "ce_2021": "https://www.cebraspe.org.br/concursos/SEFAZ_CE_21",
        "df_2020": "https://www.cebraspe.org.br/concursos/SEEC_AUDITOR_19",
        "rn": "https://www.cebraspe.org.br/concursos/SEFAZ_RN_25_AUDITOR",
        "df": "https://www.cebraspe.org.br/concursos/SEFAZ_DF_25_AUDITOR",
        # DF
    }

    def __init__(self, headless=False):
        self.driver, self.wait = get_uc_driver(headless)

    def get_url(self, fonte="gran", uf="df", verbose=False):
        if "fcc" in fonte:
            url = self.FCC_URL[uf]
        elif fonte == "cebraspe":
            url = self.CEBRASPE_URL[uf]
        elif fonte == "cebraspe_novos":
            url = "https://www.cebraspe.org.br/concursos/novos"
        else:
            # GRAN
            if uf == "pa":
                url_base = (
                    "https://blog.grancursosonline.com.br/concurso-sefa-{}/#situacao"
                )
                url = url_base.format(uf)
            else:
                url_base = (
                    "https://blog.grancursosonline.com.br/concurso-sefaz-{}/#situacao"
                )
                url = url_base.format(uf)

        if verbose:
            print("{} url: {}".format(fonte, url))

        return url

    # @retry(
    #     stop=stop_after_attempt(1),
    #     wait=wait_fixed(1),
    #     retry=retry_if_exception_type(Exception),
    # )
    def busca_novidade(self, fonte="cebraspe", uf="df", verbose=False):
        url = self.get_url(fonte, uf, verbose=verbose)

        # Acessa a página protegida
        self.driver.get(url)

        # Espera resposta
        self.wait_load(verbose=verbose)

        lista_noticias = []
        for list_text in np.list_text(self.driver, fonte=fonte, verbose=verbose):
            registro = np.rec_from_text(list_text, uf, fonte=fonte, url=url)

            # Consulta Banco de dados
            db = Storage()
            lista_resultados = db.read(registro["hashid"], fonte=fonte, verbose=verbose)
            if len(lista_resultados) == 0:
                db.insert(registro, fonte=fonte, verbose=verbose)
                if verbose:
                    print(uf, registro["txcompleto"])
            else:
                if verbose:
                    print(".", end=".")

            lista_noticias.append(registro)

        if verbose:
            print("busca_novidade", fonte, uf)

    def busca_lista(self, fonte="gran", lista_uf=["df"], verbose=False):
        for uf in lista_uf:
            self.busca_novidade(fonte=fonte, uf=uf, verbose=verbose)

        if verbose:
            print("busca_lista", fonte, lista_uf)

    # Espera resposta
    def wait_load(self, timeout=20, verbose=False):
        last_count = -1
        start_time = time.time()
        retry_timeout = 0.5

        # Pode ser parametro da função
        selector = "div"

        while True:
            page_state = self.driver.execute_script("return document.readyState;")
            if page_state == "complete":
                break
            time.sleep(retry_timeout)

        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

        while time.time() - start_time < timeout:
            current_count = len(self.driver.find_elements(By.CSS_SELECTOR, selector))
            if current_count > 0 and current_count == last_count:
                if verbose:
                    print(
                        "Pagina Estabilizada. [readyState]: {} [count elements]: {}".format(
                            page_state, current_count
                        )
                    )
                return True  # O número de elementos estabilizou
            else:
                if verbose:
                    print(
                        "Pagina não estabilizada. [readyState]: {} [count elements]: {}".format(
                            page_state, current_count
                        )
                    )
            last_count = current_count
            time.sleep(retry_timeout)

        print("Ocorreu Timeout e os elementos não estabilizaram.")

        return False

# from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
import time

from .browser import get_uc_driver
from .parser import NoticiasParser as np


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

    def get_url(self, fonte='gran',uf="df", verbose=False):
        if fonte == 'fcc':
            url = self.FCC_URL[uf]
        elif fonte == 'cebraspe':
            url = self.CEBRASPE_URL[uf]
        elif fonte == 'cebraspe_novos':
            url = "https://www.cebraspe.org.br/concursos/novos"
        else:
            # GRAN
            if uf == "pa":
                url_base = "https://blog.grancursosonline.com.br/concurso-sefa-{}/#situacao"
                url = url_base.format(uf)
            else:
                url_base = (
                    "https://blog.grancursosonline.com.br/concurso-sefaz-{}/#situacao"
                )
                url = url_base.format(uf)

        if not verbose:
            print("{} url: {}".format(fonte,uf))
        
        return url

    def busca_novidade(self, fonte="cebraspe", uf='df', verbose=False):
        url = self.get_url(fonte,uf,verbose)

        # Acessa a página protegida
        self.driver.get(url)

        # Espera resposta
        self.wait_load()

        lista_noticias = []
        for elemento_texto in np.list_text(self.driver, fonte=fonte, verbose=verbose):
            registro = get_registro_from_texto(
                elemento_texto, sefaz, fonte=fonte, url=url
            )

            # Consulta Banco de dados
            # print(registro['hashid'],fonte)
            lista_resultados = get_registro(
                registro["hashid"], string_banco, fonte=fonte
            )
            if len(lista_resultados) == 0:
                insere_registro(registro, string_banco, fonte=fonte)
                if not modo_silencioso:
                    print(sefaz, registro["txcompleto"])
            else:
                if not modo_silencioso:
                    print(".", end=".")

            lista_noticias.append(registro)

        if not modo_silencioso:
            print()


    def busca_novidade(self, fonte="gran", lista_uf=["df"], verbose=False):
        self.get_url(fonte,uf,verbose)

        # Acessa a página protegida
        self.driver.get(url)

        # Espera resposta
        self.wait_load()

        for sefaz in lista_sefaz:




    # Espera resposta
    def wait_load(self, timeout=20):
        last_count = -1
        start_time = time.time()
        retry_timeout = 0.5

        # Pode ser parametro da função
        selector = "table tr"

        while True:
            page_state = self.driver.execute_script("return document.readyState;")
            if page_state == "complete":
                break
            time.sleep(retry_timeout)

        while time.time() - start_time < timeout:
            current_count = len(self.driver.find_elements(By.CSS_SELECTOR, selector))
            if current_count > 0 and current_count == last_count:
                print(
                    "Pagina Estabilizada. [readyState]: {} [count elements]: {}".format(
                        page_state, current_count
                    )
                )
                return True  # O número de elementos estabilizou
            last_count = current_count
            time.sleep(retry_timeout)

        print("Ocorreu Timeout e os elementos não estabilizaram.")

        return False
